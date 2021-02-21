import asyncio
import ipaddress
from typing import List, Tuple

import aggregate6

import aiohttp
from databases import Database

from irrexplorer.config import RIRSTATS_URL, DATABASE_URL
from irrexplorer.state import RIR
from irrexplorer.storage.tables import rirstats

ADDRESS_FAMILY_MAPPING = {
    'ipv4': 4,
    'ipv6': 6,
}
RELEVANT_STATUSES = ['allocated', 'assigned']


class ImporterException(Exception):
    pass


class RIRStatsImporter:
    def __init__(self, rir: RIR):
        self.rir = rir

    async def run_import(self):
        url = RIRSTATS_URL[self.rir]
        text = await self._retrieve_rirstats(url)
        prefixes4, prefixes6 = self._parse_rirstats(text)
        await self._load_prefixes(prefixes4, prefixes6)

    async def _retrieve_rirstats(self, url: str):
        # TODO: create a shared session?
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise ImporterException(f'Failed import from {url}: status {response.status}')
                return await response.text()

    def _parse_rirstats(self, text: str) -> Tuple[List[str], List[str]]:
        prefixes4 = []
        prefixes6 = []
        for line in text.splitlines():
            if line.startswith('#'):  # APNIC uses comments
                continue
            if line.startswith('2|'):  # Header
                continue
            try:
                rir, country, af_string, start_ip, size, date, status = line.split('|')[:7]
            except ValueError:
                if line.split('|')[-1] == 'summary':
                    continue
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
                prefixes6.append(f'{start_ip}/{size}')

        return aggregate6.aggregate(prefixes4), aggregate6.aggregate(prefixes6)
        # return [], aggregate6.aggregate(prefixes6)

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
                        query=rirstats.insert(),
                        values=prefixes_to_insert(4, prefixes4)
                    )
                if prefixes6:
                    await database.execute_many(
                        query=rirstats.insert(),
                        values=prefixes_to_insert(6, prefixes6)
                    )


async def main():
    for rir in RIR:
        print(f'Starting {rir}')
        await RIRStatsImporter(rir).run_import()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
