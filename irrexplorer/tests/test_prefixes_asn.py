from os import environ

import pytest

from irrexplorer.state import RIR
from irrexplorer.storage import tables

pytestmark = pytest.mark.asyncio

IRRD_PREFIX_EMPTY_RESPONSE = {"data": {"rpslObjects": []}}  # type: ignore

IRRD_PREFIX_VALID_RESPONSE = {
    "data": {
        "rpslObjects": [
            {
                "rpslPk": "192.0.2.0/24AS64501",
                "objectClass": "route",
                "prefix": "192.0.2.0/24",
                "asn": 64501,
                "source": "TESTDB",
                "rpkiStatus": "invalid",
                "rpkiMaxLength": None,
            },
            {
                "rpslPk": "192.0.2.0/24AS64502ML24",
                "objectClass": "route",
                "prefix": "192.0.2.0/24",
                "asn": 64502,
                "source": "RPKI",
                "rpkiStatus": "valid",
                "rpkiMaxLength": 24,
            },
        ]
    }
}


async def test_asn_invalid(client):
    response = await client.get("/api/prefixes/asn/invalid")
    assert response.status_code == 404


async def test_asn_valid(client, httpserver):
    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    httpserver.expect_request("/graphql").respond_with_json(IRRD_PREFIX_VALID_RESPONSE)

    await client.app.state.database.execute(
        query=tables.rirstats.insert(),
        values={"ip_version": 4, "prefix": "192.0.0.0/8", "rir": RIR.RIPENCC},
    )
    await client.app.state.database.execute_many(
        query=tables.bgp.insert(),
        values=[
            {"ip_version": 4, "prefix": "192.0.2.0/24", "asn": 64500},
            {"ip_version": 4, "prefix": "192.0.2.128/25", "asn": 64501},
        ],
    )

    response = await client.get("/api/prefixes/asn/64500")
    assert response.status_code == 200

    expected = {
        "directOrigin": [
            {
                "prefix": "192.0.2.0/24",
                "prefixSortKey": "3221225984/24",
                "goodnessOverall": 0,
                "categoryOverall": "danger",
                "bgpOrigins": [64500],
                "specialUseType": None,
                "rir": "RIPE NCC",
                "rpkiRoutes": [
                    {
                        "rpkiMaxLength": 24,
                        "rpkiStatus": "VALID",
                        "asn": 64502,
                        "rpslPk": "192.0.2.0/24AS64502ML24",
                    }
                ],
                "irrRoutes": {
                    "TESTDB": [
                        {
                            "rpkiMaxLength": None,
                            "rpkiStatus": "INVALID",
                            "asn": 64501,
                            "rpslPk": "192.0.2.0/24AS64501",
                        }
                    ]
                },
                "messages": [
                    {"category": "danger", "text": "No route objects match DFZ origin"},
                    {"category": "danger", "text": "RPKI origin does not match BGP origin"},
                    {"category": "danger", "text": "RPKI invalid route objects found"},
                    {
                        "category": "warning",
                        "text": "Expected route object in RIPE, but only found in other IRRs",
                    },
                ],
            }
        ],
        "overlaps": [
            {
                "prefix": "192.0.2.128/25",
                "prefixSortKey": "3221226112/25",
                "goodnessOverall": 0,
                "categoryOverall": "danger",
                "bgpOrigins": [64501],
                "specialUseType": None,
                "rir": "RIPE NCC",
                "rpkiRoutes": [],
                "irrRoutes": {},
                "messages": [
                    {"category": "danger", "text": "No route objects match DFZ origin"},
                    {"category": "info", "text": "No (covering) RPKI ROA found for route objects"},
                ],
            }
        ],
    }

    assert response.json() == expected


async def test_asn_no_data(client, httpserver):
    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    httpserver.expect_request("/graphql").respond_with_json(IRRD_PREFIX_EMPTY_RESPONSE)

    await client.app.state.database.execute(
        query=tables.bgp.insert(),
        values={"ip_version": 4, "prefix": "192.0.2.0/24", "asn": 64500},
    )

    response = await client.get("/api/prefixes/asn/64500")
    assert response.status_code == 200
    expected = {
        "directOrigin": [
            {
                "prefix": "192.0.2.0/24",
                "prefixSortKey": "3221225984/24",
                "goodnessOverall": 0,
                "categoryOverall": "danger",
                "bgpOrigins": [64500],
                "rir": None,
                "specialUseType": None,
                "rpkiRoutes": [],
                "irrRoutes": {},
                "messages": [
                    {"category": "danger", "text": "No route objects match DFZ origin"},
                    {"category": "info", "text": "No (covering) RPKI ROA found for route objects"},
                ],
            }
        ],
        "overlaps": [],
    }
    assert response.json() == expected
