import ipaddress
from typing import List

import aggregate6
from asgiref.sync import sync_to_async
from databases import Database

from irrexplorer.backends.common import LocalSQLQueryBase, retrieve_url_text
from irrexplorer.exceptions import ImporterError
from irrexplorer.settings import DATABASE_URL, RIRSTATS_URL
from irrexplorer.state import RIR, DataSource
from irrexplorer.storage import tables

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
        text = await retrieve_url_text(url)
        prefixes4, prefixes6 = await self._parse_rirstats(text)
        await self._load_prefixes(prefixes4, prefixes6)

    @sync_to_async
    def _parse_rirstats(self, text: str):
        prefixes4 = []
        prefixes6 = []
        for ip_version, start_ip, size in self._rirstats_lines(text):
            if ip_version == 4:
                first_ip = ipaddress.ip_address(start_ip)
                last = int(first_ip) + int(size) - 1
                last_ip = ipaddress.ip_address(last)
                cidrs = ipaddress.summarize_address_range(first_ip, last_ip)
                for prefix in cidrs:
                    prefixes4.append(str(prefix))
            else:
                prefixes6.append(f"{start_ip}/{size}")

        return aggregate6.aggregate(prefixes4), aggregate6.aggregate(prefixes6)

    def _rirstats_lines(self, text: str):
        """
        Read RIRstats lines from the RIRstats in `text`.
        Returns a generator producing tuples with ip_version, start ip and size.
        """
        for line in text.splitlines():
            if not line or line.startswith("#") or line.startswith("2|"):
                continue  # Comments or header

            try:
                # ARIN includes a signature, so extra fields are ignored
                rir, country, af_string, start_ip, size, date, status = line.split("|")[:7]
            except ValueError:
                if line.split("|")[-1] == "summary":
                    continue  # The summary line has a different length and can be ignored
                raise ImporterError(f"Invalid rirstats line: {line.split('|')}")

            if status not in RELEVANT_STATUSES:
                continue

            try:
                ip_version = ADDRESS_FAMILY_MAPPING[af_string]
            except KeyError:
                continue

            yield ip_version, start_ip, size

    async def _load_prefixes(self, prefixes4: List[str], prefixes6: List[str]):
        def prefixes_to_sql_values(ip_version, prefixes):
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
                query = tables.rirstats.delete(tables.rirstats.c.rir == self.rir)
                await database.execute(query)
                if prefixes4:
                    await database.execute_many(
                        query=tables.rirstats.insert(), values=prefixes_to_sql_values(4, prefixes4)
                    )
                if prefixes6:
                    await database.execute_many(
                        query=tables.rirstats.insert(), values=prefixes_to_sql_values(6, prefixes6)
                    )


class RIRStatsQuery(LocalSQLQueryBase):
    source = DataSource.RIRSTATS
    table = tables.rirstats
    prefix_info_field = "rir"
