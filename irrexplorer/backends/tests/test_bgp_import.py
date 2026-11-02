from ipaddress import IPv4Network, IPv6Network

import pytest
from databases import Database

from irrexplorer.exceptions import ImporterError
from irrexplorer.settings import DATABASE_URL
from irrexplorer.storage import tables

from .. import bgp
from ..bgp import BGPImporter

pytestmark = pytest.mark.asyncio

VALID_BGP_BODY = """
{"CIDR":"::/0","ASN":64500,"Hits":10}
{"CIDR":"2001:db8::/32","ASN":4200000000,"Hits":1000}
{"CIDR":"2001:db8::/128","ASN":4200000001,"Hits":1000}
{"CIDR":"192.0.2.0/24","ASN":64500,"Hits":1000}
{"CIDR":"192.0.2.0/32","ASN":64501,"Hits":1000}
"""


def mock_bgp_source(httpserver, monkeypatch, body, status=200):
    monkeypatch.setattr(bgp, "BGP_SOURCE", httpserver.url_for("/bgp"))
    httpserver.expect_oneshot_request("/bgp").respond_with_data(body, status=status)


async def test_importer_valid(httpserver, monkeypatch):
    mock_bgp_source(httpserver, monkeypatch, VALID_BGP_BODY)
    await BGPImporter().run_import()

    async with Database(DATABASE_URL) as database:
        rows = await database.fetch_all(query=tables.bgp.select())
        results = [dict(r) for r in rows]
        assert results == [
            {"asn": 4200000000, "prefix": IPv6Network("2001:db8::/32")},
            {"asn": 64500, "prefix": IPv4Network("192.0.2.0/24")},
        ]
        await database.execute(query=tables.bgp.delete())


async def test_importer_invalid_json(httpserver, monkeypatch):
    mock_bgp_source(
        httpserver, monkeypatch, """{"CIDR":"192.0.2.0/24","ASN":64500,Hits":1000}"""
    )
    with pytest.raises(ImporterError):
        await BGPImporter().run_import()


async def test_importer_invalid_prefix(httpserver, monkeypatch):
    mock_bgp_source(httpserver, monkeypatch, """{"CIDR":"invalid","ASN":64500,"Hits":1000}""")
    with pytest.raises(ImporterError):
        await BGPImporter().run_import()


async def test_importer_invalid_prefix_ip(httpserver, monkeypatch):
    mock_bgp_source(httpserver, monkeypatch, """{"CIDR":"invalid/24","ASN":64500,"Hits":1000}""")
    with pytest.raises(ImporterError):
        await BGPImporter().run_import()


async def test_importer_404(httpserver, monkeypatch):
    mock_bgp_source(httpserver, monkeypatch, "not found", status=404)
    with pytest.raises(ImporterError):
        await BGPImporter().run_import()
