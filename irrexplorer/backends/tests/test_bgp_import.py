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
{"CIDR":"::/0","ASN":64500,"Hits":10}
{"CIDR":"2001:db8::/32","ASN":4200000000,"Hits":1000}
{"CIDR":"2001:db8::/128","ASN":4200000001,"Hits":1000}
{"CIDR":"192.0.2.0/24","ASN":64500,"Hits":1000}
{"CIDR":"192.0.2.0/32","ASN":64501,"Hits":1000}
"""


async def test_importer_valid():
    with aioresponses() as http_mock:
        http_mock.get(BGP_SOURCE, status=200, body=VALID_BGP_BODY)
        await BGPImporter().run_import()

    async with Database(DATABASE_URL) as database:
        rows = await database.fetch_all(query=tables.bgp.select())
        results = [dict(r) for r in rows]
        assert results == [
            {"asn": 4200000000, "prefix": IPv6Network("2001:db8::/32")},
            {"asn": 64500, "prefix": IPv4Network("192.0.2.0/24")},
        ]
        await database.execute(query=tables.bgp.delete())


async def test_importer_invalid_json():
    with aioresponses() as http_mock:
        http_mock.get(
            BGP_SOURCE, status=200, body="""{"CIDR":"192.0.2.0/24","ASN":64500,Hits":1000}"""
        )
        with pytest.raises(ImporterError):
            await BGPImporter().run_import()


async def test_importer_invalid_prefix():
    with aioresponses() as http_mock:
        http_mock.get(BGP_SOURCE, status=200, body="""{"CIDR":"invalid","ASN":64500,"Hits":1000}""")
        with pytest.raises(ImporterError):
            await BGPImporter().run_import()


async def test_importer_invalid_prefix_ip():
    with aioresponses() as http_mock:
        http_mock.get(
            BGP_SOURCE, status=200, body="""{"CIDR":"invalid/24","ASN":64500,"Hits":1000}"""
        )
        with pytest.raises(ImporterError):
            await BGPImporter().run_import()


async def test_importer_404():
    with aioresponses() as http_mock:
        http_mock.get(BGP_SOURCE, status=404)
        with pytest.raises(ImporterError):
            await BGPImporter().run_import()
