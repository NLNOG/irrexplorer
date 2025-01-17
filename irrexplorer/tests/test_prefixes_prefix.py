from os import environ

from irrexplorer.state import RIR
from irrexplorer.storage import tables

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


IRRD_PREFIX_VALID_RESPONSE_RPKI_AS0 = {
    "data": {
        "rpslObjects": [
            {
                "rpslPk": "192.0.2.0/24AS0ML24",
                "objectClass": "route",
                "prefix": "192.0.2.0/24",
                "asn": 0,
                "source": "RPKI",
                "rpkiStatus": "valid",
                "rpkiMaxLength": 24,
                "objectText": "rpsl object text",
            },
        ]
    }
}


async def test_prefix_invalid(client):
    response = await client.get("/api/prefixes/prefix/invalid")
    assert response.status_code == 400
    assert "does not appear to be an" in response.text


async def test_prefix_too_large(client):
    response = await client.get("/api/prefixes/prefix/192.0.0.0/8")
    assert response.status_code == 200
    assert response.json() == []


async def test_prefix_valid(client, httpserver):
    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    httpserver.expect_oneshot_request("/graphql").respond_with_json(IRRD_PREFIX_VALID_RESPONSE)

    await client.app.state.database.execute(
        query=tables.rirstats.insert(),
        values={"prefix": "192.0.0.0/8", "rir": RIR.RIPENCC},
    )
    await client.app.state.database.execute(
        query=tables.rirstats.insert(),
        values={"prefix": "192.0.0.0/9", "rir": RIR.REGISTROBR},
    )
    await client.app.state.database.execute(
        query=tables.rirstats.insert(),
        values={"prefix": "192.0.0.0/7", "rir": RIR.RIPENCC},
    )
    await client.app.state.database.execute(
        query=tables.bgp.insert(),
        values={"prefix": "192.0.2.0/24", "asn": 64500},
    )

    response = await client.get("/api/prefixes/prefix/192.0.2.0/24")
    assert response.status_code == 200
    expected = [
        {
            "prefix": "192.0.2.0/24",
            "prefixSortKeyIpPrefix": "3221225984/24",
            "prefixSortKeyReverseNetworklenIp": "104-3221225984",
            "goodnessOverall": 0,
            "categoryOverall": "danger",
            "bgpOrigins": [64500],
            "rir": "Registro.BR",
            "rpkiRoutes": [
                {
                    "rpkiStatus": "VALID",
                    "asn": 64502,
                    "rpslPk": "192.0.2.0/24AS64502ML24",
                    "rpkiMaxLength": 24,
                    "rpslText": "rpsl object text",
                }
            ],
            "irrRoutes": {
                "TESTDB": [
                    {
                        "rpkiStatus": "INVALID",
                        "asn": 64501,
                        "rpslPk": "192.0.2.0/24AS64501",
                        "rpkiMaxLength": None,
                        "rpslText": "rpsl object text",
                    }
                ],
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
                    "text": "Expected route object in TC, but only found in other IRRs",
                },
            ],
        }
    ]

    assert response.json() == expected


async def test_prefix_valid_rpki_as0(client, httpserver):
    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    httpserver.expect_oneshot_request("/graphql").respond_with_json(
        IRRD_PREFIX_VALID_RESPONSE_RPKI_AS0
    )

    response = await client.get("/api/prefixes/prefix/192.0.2.0/24")
    assert response.status_code == 200
    expected = [
        {
            "prefix": "192.0.2.0/24",
            "prefixSortKeyIpPrefix": "3221225984/24",
            "prefixSortKeyReverseNetworklenIp": "104-3221225984",
            "goodnessOverall": 0,
            "categoryOverall": "danger",
            "bgpOrigins": [],
            "rir": None,
            "rpkiRoutes": [
                {
                    "rpkiStatus": "VALID",
                    "asn": 0,
                    "rpslPk": "192.0.2.0/24AS0ML24",
                    "rpkiMaxLength": 24,
                    "rpslText": "rpsl object text",
                }
            ],
            "irrRoutes": {},
            "messages": [
                {
                    "category": "danger",
                    "text": "Overlaps with RFC5737 special use prefix 192.0.2.0/24",
                },
            ],
        },
    ]

    assert response.json() == expected


async def test_prefix_no_data(client, httpserver):
    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    httpserver.expect_oneshot_request("/graphql").respond_with_json(IRRD_PREFIX_EMPTY_RESPONSE)

    await client.app.state.database.execute(
        query=tables.bgp.insert(),
        values={"prefix": "192.0.2.0/24", "asn": 64500},
    )

    response = await client.get("/api/prefixes/prefix/192.0.2.0/24")
    assert response.status_code == 200
    expected = [
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
    ]
    assert response.json() == expected
