from ipaddress import IPv4Network, IPv6Network

import pytest
from aioresponses import aioresponses
from databases import Database

from irrexplorer.exceptions import ImporterError
from irrexplorer.settings import DATABASE_URL, REGISTROBR_URL
from irrexplorer.state import RIR
from irrexplorer.storage import tables
from ..registro import RegistroRirImporter

VALID_ASN_BLK = """
AS64500|orgname1|orgid1|2001:610:2b::/63
AS64501|orgname2|orgid2|192.0.2.0/24|192.0.2.2/32|198.51.100.0/24
AS64502|orgname3|orgid3|198.51.100.0/25
"""


async def test_importer_valid():
    with aioresponses() as http_mock:
        http_mock.get(REGISTROBR_URL, status=200, body=VALID_ASN_BLK)
        await RegistroRirImporter().run_import()

    async with Database(DATABASE_URL) as database:
        rows = await database.fetch_all(query=tables.rirstats.select())
        results = [dict(r) for r in rows]
        assert results == [
            {"rir": RIR.REGISTROBR, "prefix": IPv4Network("192.0.2.0/24")},
            {"rir": RIR.REGISTROBR, "prefix": IPv4Network("198.51.100.0/24")},
            {"rir": RIR.REGISTROBR, "prefix": IPv6Network("2001:610:2b::/63")},
        ]
        await database.execute(query=tables.rirstats.delete())


async def test_importer_invalid():
    with aioresponses() as http_mock:
        http_mock.get(REGISTROBR_URL, status=200, body="asn|orgname|orgid|invalid-ip")
        with pytest.raises(ImporterError):
            await RegistroRirImporter().run_import()


async def test_importer_404():
    with aioresponses() as http_mock:
        http_mock.get(REGISTROBR_URL, status=404)
        with pytest.raises(ImporterError):
            await RegistroRirImporter().run_import()
