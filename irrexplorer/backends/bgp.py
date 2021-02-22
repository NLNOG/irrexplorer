from typing import List, Tuple

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from asgiref.sync import sync_to_async
from databases import Database

from backends.utils import retrieve_url_text
from irrexplorer.config import (BGP_IPV4_LENGTH_CUTOFF, BGP_IPV6_LENGTH_CUTOFF, BGP_SOURCE,
                                DATABASE_URL)
from irrexplorer.exceptions import ImporterException
from irrexplorer.state import DataSource, IPNetwork, RouteInfo
from irrexplorer.storage.tables import bgp


class BGPImporter:
    """
    BGP origin importer.
    Retrieves origin data from BGP_SOURCE, parses it, and loads it into the SQL db.
    """
    async def run_import(self):
        url = BGP_SOURCE
        text = await retrieve_url_text(url)
        prefixes = await self._parse_table(text)
        await self._load_prefixes(prefixes)

    @sync_to_async
    def _parse_table(self, text: str):
        prefixes = []
        for line in text.splitlines():
            try:
                prefix, origin_str = line.split(" ")
                origin = int(origin_str)
            except ValueError:
                raise ImporterException(f"Invalid BGP line: {line.split('|')}")

            if self._include_route(prefix):
                prefixes.append((prefix.version, str(prefix), origin))
        return prefixes

    def _include_route(self, prefix) -> bool:
        # Filter out router to router links and other tiny blocks
        # Uses text parsing for performance
        length = int(prefix.split("/")[1])
        return length < BGP_IPV4_LENGTH_CUTOFF or (
            ":" in prefix and length < BGP_IPV6_LENGTH_CUTOFF
        )

    async def _load_prefixes(self, prefixes: List[Tuple[int, str, int]]):
        async with Database(DATABASE_URL) as database:
            async with database.transaction():
                await database.execute(bgp.delete())
                if prefixes:
                    values = [
                        {
                            "ip_version": ip_version,
                            "asn": asn,
                            "prefix": prefix,
                        }
                        for ip_version, prefix, asn in prefixes
                    ]
                    await database.execute_many(query=bgp.insert(), values=values)


class BGPQuery:
    async def query_asn(self, asn: int):
        # TODO: share database pool
        async with Database(DATABASE_URL) as database:
            async with database.transaction():
                query = bgp.select(bgp.c.asn == asn)
                result = await database.fetch_all(query=query)
                print(result[0]["prefix"])

    async def query_prefix(self, prefix: IPNetwork):
        print("running BGP")
        results = []
        async with Database(DATABASE_URL) as database:
            print("connected BGP")
            # TODO: extract common SQL
            prefix_cidr = sa.cast(str(prefix), pg.CIDR)
            query = bgp.select(
                sa.and_(
                    sa.or_(
                        bgp.c.prefix.op("<<=")(prefix_cidr),
                        bgp.c.prefix.op(">>")(prefix_cidr),
                    ),
                    bgp.c.ip_version == prefix.version,
                )
            )
            async for row in database.iterate(query=query):
                results.append(
                    RouteInfo(
                        source=DataSource.BGP,
                        prefix=row["prefix"],
                        asn=row["asn"],
                    )
                )
        print("completed BGP")
        return results
