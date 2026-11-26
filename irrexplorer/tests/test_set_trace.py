import time
from os import environ

import pytest
from werkzeug import Response

from irrexplorer.api import queries

pytestmark = pytest.mark.asyncio


def _route(prefix, asn, source="TESTDB", rpki_status="not_found", max_length=None):
    object_class = "route6" if ":" in prefix else "route"
    return {
        "rpslPk": f"{prefix}AS{asn}",
        "objectClass": object_class,
        "prefix": prefix,
        "asn": asn,
        "source": source,
        "rpkiStatus": rpki_status,
        "rpkiMaxLength": max_length,
        "objectText": "rpsl object text",
    }


def _irrd_response(routes, sets):
    # The mock server answers every GraphQL query with the same response,
    # so it carries both the route objects and the set members.
    return {
        "data": {
            "rpslObjects": routes,
            "recursiveSetMembers": [
                {"rpslPk": name, "rootSource": source, "members": members}
                for name, members_per_source in sets.items()
                for source, members in members_per_source.items()
            ],
        }
    }


DEMO_SETS = {
    "AS-DEMO-1": {"DEMO": ["AS64500", "AS-DEMO-2", "AS-DEMO-3"]},
    # lower case member: RPSL names are case insensitive
    "AS-DEMO-2": {"DEMO": ["as64501"]},
    "AS-DEMO-3": {"DEMO": ["AS-DEMO-2"], "OTHER": ["AS64501"]},
}


async def test_trace_prefix(client, httpserver):
    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    routes = [
        _route("2001:db8::/48", 64501),
        _route("2001:db8::/32", 64501, source="RPKI", rpki_status="valid", max_length=48),
        _route("2001:db8::/32", 64503),
        # more specific than the query: does not cover it
        _route("2001:db8::/56", 64502),
        # RPKI AS0 has no origin to trace
        _route("2001:db8::/32", 0, source="RPKI", rpki_status="valid", max_length=48),
        # neither of these covers the prefix
        _route("2001:db9::/32", 64504),
        _route("192.0.2.0/24", 64505),
    ]
    httpserver.expect_request("/graphql").respond_with_json(_irrd_response(routes, DEMO_SETS))

    response = await client.get("/api/sets/trace/as-demo-1/2001:db8::/48")
    assert response.status_code == 200
    data = response.json()

    assert data["target"] == "AS-DEMO-1"
    assert data["query"] == "2001:db8::/48"
    assert data["setFound"] is True
    assert data["origins"] == [64501, 64503]
    assert [(r["prefix"], r["asn"], r["source"]) for r in data["routes"]] == [
        ("2001:db8::/32", 64501, "RPKI"),
        ("2001:db8::/32", 64503, "TESTDB"),
        ("2001:db8::/48", 64501, "TESTDB"),
    ]
    assert data["paths"] == [
        {"asn": 64501, "source": "DEMO", "path": ["AS-DEMO-1", "AS-DEMO-2", "AS64501"]},
        {"asn": 64501, "source": "OTHER", "path": ["AS-DEMO-1", "AS-DEMO-3", "AS64501"]},
        {
            "asn": 64501,
            "source": "DEMO",
            "path": ["AS-DEMO-1", "AS-DEMO-3", "AS-DEMO-2", "AS64501"],
        },
    ]
    assert data["notIncluded"] == [64503]


async def test_trace_asn_direct_member(client, httpserver):
    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    httpserver.expect_request("/graphql").respond_with_json(_irrd_response([], DEMO_SETS))

    response = await client.get("/api/sets/trace/AS-DEMO-1/AS64500")
    assert response.status_code == 200
    data = response.json()
    assert data["origins"] == [64500]
    assert data["routes"] == []
    assert data["paths"] == [{"asn": 64500, "source": "DEMO", "path": ["AS-DEMO-1", "AS64500"]}]
    assert data["notIncluded"] == []


async def test_trace_unknown_set(client, httpserver):
    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    httpserver.expect_request("/graphql").respond_with_json(_irrd_response([], {}))

    response = await client.get("/api/sets/trace/AS-DEMO-MISSING/64500")
    assert response.status_code == 200
    data = response.json()
    assert data["setFound"] is False
    assert data["paths"] == []
    assert data["notIncluded"] == [64500]


async def test_trace_prefix_without_routes(client, httpserver):
    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    httpserver.expect_oneshot_request("/graphql").respond_with_json(_irrd_response([], DEMO_SETS))

    response = await client.get("/api/sets/trace/AS-DEMO-1/192.0.2.0/24")
    assert response.status_code == 200
    data = response.json()
    assert data["origins"] == []
    # Nothing to trace, so the set is not expanded
    assert data["setFound"] is None


@pytest.mark.parametrize(
    "url",
    [
        "/api/sets/trace/192.0.2.0/24/AS64500",  # target is not a set
        "/api/sets/trace/AS-DEMO-1/AS-DEMO-2",  # a set can not be traced
        "/api/sets/trace/RS-DEMO/AS64500",  # route-sets do not contain ASNs
        "/api/sets/trace/AS-DEMO-1/not a query",
    ],
)
async def test_trace_invalid(client, url):
    response = await client.get(url)
    assert response.status_code == 400


async def test_trace_timeout(client, httpserver, monkeypatch):
    def slow_handler(request):
        time.sleep(0.3)
        return Response("{}", content_type="application/json")

    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    httpserver.expect_request("/graphql").respond_with_handler(slow_handler)
    monkeypatch.setattr(queries, "SET_EXPANSION_TIMEOUT", 0.1)

    response = await client.get("/api/sets/trace/AS-DEMO-1/AS64500")
    assert response.status_code == 504
    assert "timed out" in response.text
