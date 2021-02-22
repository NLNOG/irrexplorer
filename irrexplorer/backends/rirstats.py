import ipaddress
from typing import List

import aggregate6
import aiohttp
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from asgiref.sync import sync_to_async
from databases import Database

from irrexplorer.config import DATABASE_URL, RIRSTATS_URL
from irrexplorer.exceptions import ImporterException
from irrexplorer.state import RIR, DataSource, RouteInfo, IPNetwork
from irrexplorer.storage.tables import rirstats

ADDRESS_FAMILY_MAPPING = {
    "ipv4": 4,
    "ipv6": 6,
}
RELEVANT_STATUSES = ["allocated", "assigned"]


class RIRStatsImporter:
    def __init__(self, rir: RIR):
        self.rir = rir

    async def run_import(self):
        url = RIRSTATS_URL[self.rir]
        print(f"retrieving {self.rir}")
        text = await self._retrieve_rirstats(url)
        print(f"parsing {self.rir}")
        prefixes4, prefixes6 = await self._parse_rirstats(text)
        print(f"loading {self.rir}")
        await self._load_prefixes(prefixes4, prefixes6)
        print(f"done {self.rir}")

    async def _retrieve_rirstats(self, url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise ImporterException(f"Failed import from {url}: status {response.status}")
                return await response.text()

    @sync_to_async
    def _parse_rirstats(self, text: str):
        prefixes4 = []
        prefixes6 = []
        for line in text.splitlines():
            if line.startswith("#") or line.startswith("2|"):
                continue  # Comments or header
            try:
                # ARIN includes a signature, so extra fields are ignored
                rir, country, af_string, start_ip, size, date, status = line.split("|")[:7]
            except ValueError:
                if line.split("|")[-1] == "summary":
                    continue  # The summary line has a different length and can be ignored
                raise ImporterException(f"Invalid rirstats line: {line.split('|')}")

            if status not in RELEVANT_STATUSES:
                continue

            try:
                address_family = ADDRESS_FAMILY_MAPPING[af_string]
            except KeyError:
                continue

            if address_family == 4:
                first_ip = ipaddress.ip_address(start_ip)
                last = int(first_ip) + int(size) - 1
                last_ip = ipaddress.ip_address(last)
                cidrs = ipaddress.summarize_address_range(first_ip, last_ip)
                for prefix in cidrs:
                    prefixes4.append(str(prefix))
            else:
                prefixes6.append(f"{start_ip}/{size}")

        return aggregate6.aggregate(prefixes4), aggregate6.aggregate(prefixes6)

    async def _load_prefixes(self, prefixes4: List[str], prefixes6: List[str]):
        def prefixes_to_insert(ip_version, prefixes):
            return [
                {
                    "ip_version": ip_version,
                    "rir": self.rir,
                    "prefix": prefix,
                }
                for prefix in prefixes
            ]

        async with Database(DATABASE_URL) as database:
            async with database.transaction():
                query = rirstats.delete(rirstats.c.rir == self.rir)
                await database.execute(query)
                if prefixes4:
                    await database.execute_many(
                        query=rirstats.insert(), values=prefixes_to_insert(4, prefixes4)
                    )
                if prefixes6:
                    await database.execute_many(
                        query=rirstats.insert(), values=prefixes_to_insert(6, prefixes6)
                    )


class RIRStatsQuery:
    async def query_prefix(self, prefix: IPNetwork):
        print("running rirstats")
        results = []
        async with Database(DATABASE_URL) as database:
            print("connected rirstats")
            # TODO: extract common SQL
            prefix_cidr = sa.cast(str(prefix), pg.CIDR)
            query = rirstats.select(
                sa.and_(
                    sa.or_(
                        rirstats.c.prefix.op("<<=")(prefix_cidr),
                        rirstats.c.prefix.op(">>")(prefix_cidr),
                    ),
                    rirstats.c.ip_version == prefix.version,
                )
            )
            async for row in database.iterate(query=query):
                results.append(
                    RouteInfo(
                        source=DataSource.RIRSTATS,
                        prefix=row["prefix"],
                        rir=row["rir"],
                    )
                )
        print("completed rirstats")
        return results
