import aggregate6
from asgiref.sync import sync_to_async

from irrexplorer.backends.common import retrieve_url_text, store_rir_prefixes
from irrexplorer.exceptions import ImporterError
from irrexplorer.settings import REGISTROBR_URL
from irrexplorer.state import RIR


class RegistroRirImporter:
    """
    Importer for the asn-blk format from Registro.BR/TC,
    which is treated as rirstats except for the different
    file format requiring this separate parser.
    Beyond that, it gets added to the same table and therefore
    counts as an "RIR" in all other code.
    """
    rir = RIR.REGISTROBR

    async def run_import(self):
        url = REGISTROBR_URL
        text = await retrieve_url_text(url)
        prefixes = await self._parse_registrobr(text)
        await store_rir_prefixes(self.rir, prefixes)

    @sync_to_async
    def _parse_registrobr(self, text: str):
        prefixes = []
        for line in text.strip().splitlines():
            prefixes += line.split("|")[3:]
        try:
            return aggregate6.aggregate(prefixes)
        except Exception as exc:
            if 'invalid IP prefix' in str(exc):
                raise ImporterError(f"Invalid IP: {exc}")
            raise  # pragma: no cover
