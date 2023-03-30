import aggregate6
from asgiref.sync import sync_to_async

from irrexplorer.backends.common import retrieve_url_text, store_rir_prefixes
from irrexplorer.settings import REGISTROBR_URL
from irrexplorer.state import RIR


class RegistroImporter:
    rir = RIR.REGISTROBR

    async def run_import(self):
        url = REGISTROBR_URL
        text = await retrieve_url_text(url)
        prefixes = await self._parse_registrobr(text)
        await store_rir_prefixes(self.rir, prefixes)

    @sync_to_async
    def _parse_registrobr(self, text: str):
        prefixes = []
        for line in text.splitlines():
            prefixes += line.split("|")[3:]

        return aggregate6.aggregate(prefixes)
