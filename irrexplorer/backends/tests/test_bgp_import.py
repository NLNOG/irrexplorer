from ipaddress import IPv4Network, IPv6Network

import pytest
from aioresponses import aioresponses
from databases import Database

from irrexplorer.exceptions import ImporterError
from irrexplorer.settings import BGP_SOURCE, DATABASE_URL
from irrexplorer.storage import tables

from ..bgp import BGPImporter

pytestmark = pytest.mark.asyncio

VALID_BGP_BODY = """
192.0.2.0/24 64500
192.0.2.0/32 64501
2001:db8::/32 4200000000
2001:db8::/128 4200000001
"""


async def test_importer_valid():
    with aioresponses() as http_mock:
        http_mock.get(BGP_SOURCE, status=200, body=VALID_BGP_BODY)
        await BGPImporter().run_import()

    async with Database(DATABASE_URL) as database:
        rows = await database.fetch_all(query=tables.bgp.select())
        results = [dict(r) for r in rows]
        assert results == [
            {"ip_version": 4, "asn": 64500, "prefix": IPv4Network("192.0.2.0/24")},
            {"ip_version": 6, "asn": 4200000000, "prefix": IPv6Network("2001:db8::/32")},
        ]
        await database.execute(query=tables.bgp.delete())


async def test_importer_invalid():
    with aioresponses() as http_mock:
        http_mock.get(BGP_SOURCE, status=200, body="""192.0.2.0/24 64500 invalid-extra""")
        with pytest.raises(ImporterError):
            await BGPImporter().run_import()

    with aioresponses() as http_mock:
        http_mock.get(BGP_SOURCE, status=200, body="""invalid 64500""")
        with pytest.raises(ImporterError):
            await BGPImporter().run_import()

    with aioresponses() as http_mock:
        http_mock.get(BGP_SOURCE, status=200, body="""invalid/24 64500""")
        with pytest.raises(ImporterError):
            await BGPImporter().run_import()


async def test_importer_404():
    with aioresponses() as http_mock:
        http_mock.get(BGP_SOURCE, status=404)
        with pytest.raises(ImporterError):
            await BGPImporter().run_import()
