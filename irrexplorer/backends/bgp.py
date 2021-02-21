import ipaddress
from typing import List, Tuple

import aiohttp
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from asgiref.sync import sync_to_async
from databases import Database

from irrexplorer.config import BGP_SOURCE, DATABASE_URL
from irrexplorer.exceptions import ImporterException
from irrexplorer.state import DataSource, RouteInfo
from irrexplorer.storage.tables import bgp


class BGPImporter:
    async def run_import(self):
        url = BGP_SOURCE
        print("retrieving BGP")
        text = await self._retrieve_table(url)
        print("parsing BGP")
        prefixes = await self._parse_table(text)
        print("loading BGP")
        await self._load_prefixes(prefixes)
        print("done BGP")

    async def _retrieve_table(self, url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise ImporterException(f"Failed import from {url}: status {response.status}")
                return await response.text()

    @sync_to_async
    def _parse_table(self, text: str):
        prefixes = []
        for line in text.splitlines():
            try:
                prefix_str, origin_str = line.split(" ")
                prefix = ipaddress.ip_network(prefix_str)
                origin = int(origin_str)
            except ValueError:
                raise ImporterException(f"Invalid BGP line: {line.split('|')}")

            # TODO: abstract this somewhere generic
            if prefix.version == 4 and prefix.prefixlen >= 29:
                continue
            if prefix.version == 6 and prefix.prefixlen >= 124:
                continue
            prefixes.append((prefix.version, str(prefix), origin))
        return prefixes

    async def _load_prefixes(self, prefixes: List[Tuple[int, str, int]]):
        async with Database(DATABASE_URL) as database:
            async with database.transaction():
                query = bgp.delete()
                await database.execute(query)
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

    async def query_prefix(self, ip_version: int, prefix: str):
        print("running BGP")
        results = []
        async with Database(DATABASE_URL) as database:
            print("connected BGP")
            # TODO: extract common SQL
            prefix_cidr = sa.cast(prefix, pg.CIDR)
            query = bgp.select(
                sa.and_(
                    sa.or_(
                        bgp.c.prefix.op("<<=")(prefix_cidr),
                        bgp.c.prefix.op(">>")(prefix_cidr),
                    ),
                    bgp.c.ip_version == ip_version,
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
