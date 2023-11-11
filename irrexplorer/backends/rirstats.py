import ipaddress

import aggregate6
from asgiref.sync import sync_to_async

from irrexplorer.backends.common import LocalSQLQueryBase, retrieve_url_text, store_rir_prefixes
from irrexplorer.exceptions import ImporterError
from irrexplorer.settings import RIRSTATS_URL
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
        prefixes = await self._parse_rirstats(text)
        await store_rir_prefixes(self.rir, prefixes)

    @sync_to_async
    def _parse_rirstats(self, text: str):
        prefixes = []
        for ip_version, start_ip, size in self._rirstats_lines(text):
            if ip_version == 4:
                first_ip = ipaddress.ip_address(start_ip)
                last = int(first_ip) + int(size) - 1
                last_ip = ipaddress.ip_address(last)
                cidrs = ipaddress.summarize_address_range(first_ip, last_ip)
                for prefix in cidrs:
                    prefixes.append(str(prefix))
            else:
                prefixes.append(f"{start_ip}/{size}")

        return aggregate6.aggregate(prefixes)

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


class RIRStatsQuery(LocalSQLQueryBase):
    source = DataSource.RIRSTATS
    table = tables.rirstats
    prefix_info_field = "rir"
