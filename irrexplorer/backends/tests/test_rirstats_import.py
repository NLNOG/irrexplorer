from ipaddress import IPv4Network, IPv6Network

import pytest
from databases import Database

from irrexplorer.exceptions import ImporterError
from irrexplorer.settings import DATABASE_URL
from irrexplorer.state import RIR
from irrexplorer.storage import tables

from .. import rirstats
from ..rirstats import RIRStatsImporter

VALID_RIRSTATS = """
2|ripencc|1614293940|143246|19830705|20210225|+0100
ripencc|*|ipv4|*|84420|summary
ripencc|*|asn|*|36707|summary
ripencc|*|ipv6|*|22119|summary
ripencc|EU|asn|64500|1|19930901|allocated
ripencc|EU|ipv4|192.0.2.0|256|20100625|allocated
ripencc|EU|ipv4|192.0.2.0|32|20100625|allocated
ripencc|EU|ipv4|192.0.2.128|32|20100625|allocated
ripencc|EU|ipv6|2001:610:2b::|64|20200702|assigned
ripencc|EU|ipv6|2001:610:2b:1::|64|20200702|assigned|signature-extended
ripencc|EU|ipv6|2001:610:2b::|48|20200702|ignored|signature-extended
"""


def mock_rirstats_source(httpserver, monkeypatch, body, status=200):
    monkeypatch.setitem(rirstats.RIRSTATS_URL, RIR.RIPENCC, httpserver.url_for("/rirstats"))
    httpserver.expect_oneshot_request("/rirstats").respond_with_data(body, status=status)


async def test_importer_valid(httpserver, monkeypatch):
    mock_rirstats_source(httpserver, monkeypatch, VALID_RIRSTATS)
    await RIRStatsImporter(RIR.RIPENCC).run_import()

    async with Database(DATABASE_URL) as database:
        rows = await database.fetch_all(query=tables.rirstats.select())
        results = [dict(r) for r in rows]
        assert results == [
            {"rir": RIR.RIPENCC, "prefix": IPv4Network("192.0.2.0/24")},
            {"rir": RIR.RIPENCC, "prefix": IPv6Network("2001:610:2b::/63")},
        ]
        await database.execute(query=tables.rirstats.delete())


async def test_importer_invalid(httpserver, monkeypatch):
    mock_rirstats_source(httpserver, monkeypatch, "invalid|number|fields")
    with pytest.raises(ImporterError):
        await RIRStatsImporter(RIR.RIPENCC).run_import()


async def test_importer_404(httpserver, monkeypatch):
    mock_rirstats_source(httpserver, monkeypatch, "not found", status=404)
    with pytest.raises(ImporterError):
        await RIRStatsImporter(RIR.RIPENCC).run_import()
