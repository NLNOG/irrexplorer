from typing import List, Tuple

from asgiref.sync import sync_to_async
from databases import Database

from irrexplorer.backends.common import LocalSQLQueryBase, retrieve_url_text
from irrexplorer.exceptions import ImporterException
from irrexplorer.settings import (
    BGP_IPV4_LENGTH_CUTOFF,
    BGP_IPV6_LENGTH_CUTOFF,
    BGP_SOURCE,
    DATABASE_URL,
)
from irrexplorer.state import DataSource
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

            ip_version = 6 if ":" in prefix else 4
            if self._include_route(ip_version, prefix):
                prefixes.append((ip_version, prefix, origin))
        return prefixes

    def _include_route(self, ip_version: int, prefix: str) -> bool:
        # Filter out router to router links and other tiny blocks
        # Uses text parsing for performance
        length = int(prefix.split("/")[1])
        return length < BGP_IPV4_LENGTH_CUTOFF or (
            ip_version == 6 and length < BGP_IPV6_LENGTH_CUTOFF
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


class BGPQuery(LocalSQLQueryBase):
    source = DataSource.BGP
    table = bgp
    prefix_info_field = "asn"

    async def query_asn(self, asn: int):
        query = bgp.select(bgp.c.asn == asn)
        result = await self.database.fetch_all(query=query)
        print(result[0]["prefix"])
