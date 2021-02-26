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


async def test_prefix_invalid(client):
    response = await client.get("/api/prefix/invalid")
    assert response.status_code == 400
    assert "does not appear to be an" in response.text


async def test_prefix_valid(client, httpserver):
    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    httpserver.expect_oneshot_request("/graphql").respond_with_json(IRRD_PREFIX_VALID_RESPONSE)

    await client.app.state.database.execute(
        query=tables.rirstats.insert(),
        values={"ip_version": 4, "prefix": "192.0.0.0/8", "rir": RIR.RIPENCC},
    )
    await client.app.state.database.execute(
        query=tables.bgp.insert(),
        values={"ip_version": 4, "prefix": "192.0.2.0/24", "asn": 64500},
    )

    response = await client.get("/api/prefix/192.0.2.0/24")
    assert response.status_code == 200
    expected = [
        {
            "prefix": "192.0.2.0/24",
            "prefixExploded": "192.0.2.0/24",
            "goodnessOverall": 0,
            "categoryOverall": "danger",
            "bgpOrigins": [64500],
            "rir": "RIPE NCC",
            "specialUseType": None,
            "rpkiRoutes": [
                {"rpkiStatus": "VALID", "asn": 64502, "rpslPk": "192.0.2.0/24AS64502ML24"}
            ],
            "irrRoutes": {
                "TESTDB": [
                    {"rpkiStatus": "INVALID", "asn": 64501, "rpslPk": "192.0.2.0/24AS64501"}
                ],
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
    ]

    assert response.json() == expected


async def test_prefix_no_data(client, httpserver):
    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    httpserver.expect_oneshot_request("/graphql").respond_with_json(IRRD_PREFIX_EMPTY_RESPONSE)

    await client.app.state.database.execute(
        query=tables.bgp.insert(),
        values={"ip_version": 4, "prefix": "192.0.2.0/24", "asn": 64500},
    )

    response = await client.get("/api/prefix/192.0.2.0/24")
    assert response.status_code == 200
    expected = [
        {
            "prefixExploded": "192.0.2.0/24",
            "prefix": "192.0.2.0/24",
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
    ]
    assert response.json() == expected
