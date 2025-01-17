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
                "objectText": "rpsl object text",
            },
            {
                "rpslPk": "192.0.2.0/24AS64502ML24",
                "objectClass": "route",
                "prefix": "192.0.2.0/24",
                "asn": 64502,
                "source": "RPKI",
                "rpkiStatus": "valid",
                "rpkiMaxLength": 24,
                "objectText": "rpsl object text",
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
        values={"prefix": "192.0.0.0/8", "rir": RIR.RIPENCC},
    )
    await client.app.state.database.execute_many(
        query=tables.bgp.insert(),
        values=[
            {"prefix": "192.0.2.0/24", "asn": 64500},
            {"prefix": "192.0.2.128/25", "asn": 64501},
        ],
    )

    response = await client.get("/api/prefixes/asn/64500")
    assert response.status_code == 200

    expected = {
        "directOrigin": [
            {
                "prefix": "192.0.2.0/24",
                "prefixSortKeyIpPrefix": "3221225984/24",
                "prefixSortKeyReverseNetworklenIp": "104-3221225984",
                "goodnessOverall": 0,
                "categoryOverall": "danger",
                "bgpOrigins": [64500],
                "rir": "RIPE NCC",
                "rpkiRoutes": [
                    {
                        "rpkiMaxLength": 24,
                        "rpkiStatus": "VALID",
                        "asn": 64502,
                        "rpslPk": "192.0.2.0/24AS64502ML24",
                        "rpslText": "rpsl object text",
                    }
                ],
                "irrRoutes": {
                    "TESTDB": [
                        {
                            "rpkiMaxLength": None,
                            "rpkiStatus": "INVALID",
                            "asn": 64501,
                            "rpslPk": "192.0.2.0/24AS64501",
                            "rpslText": "rpsl object text",
                        }
                    ]
                },
                "messages": [
                    {"category": "danger", "text": "No route objects match DFZ origin"},
                    {"category": "danger", "text": "RPKI origin does not match BGP origin"},
                    {"category": "danger", "text": "RPKI-invalid route objects found"},
                    {
                        "category": "danger",
                        "text": "Overlaps with RFC5737 special use prefix 192.0.2.0/24",
                    },
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
                "prefixSortKeyIpPrefix": "3221226112/25",
                "prefixSortKeyReverseNetworklenIp": "103-3221226112",
                "goodnessOverall": 0,
                "categoryOverall": "danger",
                "bgpOrigins": [64501],
                "rir": "RIPE NCC",
                "rpkiRoutes": [],
                "irrRoutes": {},
                "messages": [
                    {"category": "danger", "text": "No route objects match DFZ origin"},
                    {
                        "category": "danger",
                        "text": "Overlaps with RFC5737 special use prefix 192.0.2.0/24",
                    },
                ],
            }
        ],
    }

    assert response.json() == expected


async def test_asn_no_irr_data(client, httpserver):
    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    httpserver.expect_request("/graphql").respond_with_json(IRRD_PREFIX_EMPTY_RESPONSE)

    await client.app.state.database.execute(
        query=tables.bgp.insert(),
        values={"prefix": "192.0.2.0/24", "asn": 64500},
    )

    response = await client.get("/api/prefixes/asn/64500")
    assert response.status_code == 200
    expected = {
        "directOrigin": [
            {
                "prefix": "192.0.2.0/24",
                "prefixSortKeyIpPrefix": "3221225984/24",
                "prefixSortKeyReverseNetworklenIp": "104-3221225984",
                "goodnessOverall": 0,
                "categoryOverall": "danger",
                "bgpOrigins": [64500],
                "rir": None,
                "rpkiRoutes": [],
                "irrRoutes": {},
                "messages": [
                    {"category": "danger", "text": "No route objects match DFZ origin"},
                    {
                        "category": "danger",
                        "text": "Overlaps with RFC5737 special use prefix 192.0.2.0/24",
                    },
                ],
            }
        ],
        "overlaps": [],
    }
    assert response.json() == expected


async def test_asn_no_data(client, httpserver):
    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    httpserver.expect_request("/graphql").respond_with_json(IRRD_PREFIX_EMPTY_RESPONSE)

    response = await client.get("/api/prefixes/asn/64500")
    assert response.status_code == 200
    expected = {
        "directOrigin": [],
        "overlaps": [],
    }
    assert response.json() == expected
