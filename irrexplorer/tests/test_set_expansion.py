import time
from os import environ

import pytest
from werkzeug import Response

from irrexplorer.api import collectors, queries

pytestmark = pytest.mark.asyncio


def _set_members_response(sets):
    # Mock of recursiveSetMembers response, from {set name: {source: [members]}}
    return {
        "data": {
            "recursiveSetMembers": [
                {"rpslPk": name, "rootSource": source, "members": members}
                for name, members_per_source in sets.items()
                for source, members in members_per_source.items()
            ]
        }
    }


IRRD_SET_EMPTY_RESPONSE = _set_members_response({})

IRRD_SET_VALID_RESPONSE = _set_members_response(
    {
        "AS-DEMO-1": {"DEMO": ["AS64500", "AS-DEMO-2"]},
        "AS-DEMO-2": {"DEMO": ["AS-DEMO-3", "AS64501"]},
        "AS-DEMO-3": {"DEMO1": ["AS-DEMO-4", "AS-DEMO-1", "AS64502"], "DEMO2": ["AS64503"]},
    }
)

IRRD_DEEP_RESPONSE_MEMBERS = ["AS64500"] + [f"AS-DEMO-{i}" for i in range(2000)]
IRRD_SET_DEEP_RESPONSE = _set_members_response(
    {
        "AS-DEMO-1": {"DEMO": IRRD_DEEP_RESPONSE_MEMBERS},
        "AS-DEMO-2": {"DEMO": ["AS64501"]},
    }
)


async def test_expand_valid(client, httpserver):
    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    httpserver.expect_request("/graphql").respond_with_json(IRRD_SET_VALID_RESPONSE)

    response = await client.get("/api/sets/expand/AS-DEMO-1")
    assert response.status_code == 200
    expected = [
        {
            "name": "AS-DEMO-1",
            "depth": 1,
            "source": "DEMO",
            "path": ["AS-DEMO-1"],
            "members": ["AS-DEMO-2", "AS64500"],
        },
        {
            "name": "AS-DEMO-2",
            "depth": 2,
            "source": "DEMO",
            "path": ["AS-DEMO-1", "AS-DEMO-2"],
            "members": ["AS-DEMO-3", "AS64501"],
        },
        {
            "name": "AS-DEMO-3",
            "depth": 3,
            "source": "DEMO1",
            "path": ["AS-DEMO-1", "AS-DEMO-2", "AS-DEMO-3"],
            "members": ["AS-DEMO-1", "AS-DEMO-4", "AS64502"],
        },
        {
            "name": "AS-DEMO-3",
            "depth": 3,
            "source": "DEMO2",
            "path": ["AS-DEMO-1", "AS-DEMO-2", "AS-DEMO-3"],
            "members": ["AS64503"],
        },
    ]
    assert response.json() == expected


async def test_expand_valid_excessive_depth(client, httpserver):
    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    httpserver.expect_request("/graphql").respond_with_json(IRRD_SET_DEEP_RESPONSE)

    response = await client.get("/api/sets/expand/AS-DEMO-1")
    assert response.status_code == 200
    json = response.json()

    assert len(json) == 2
    assert json[0]["name"] == "AS-DEMO-1"
    assert set(json[0]["members"]) == set(IRRD_DEEP_RESPONSE_MEMBERS)

    assert json[1] == {
        "name": "AS-DEMO-2",
        "depth": 2,
        "source": "DEMO",
        "path": ["AS-DEMO-1", "AS-DEMO-2"],
        "members": ["AS64501"],
    }


async def test_expand_no_data(client, httpserver):
    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    httpserver.expect_request("/graphql").respond_with_json(IRRD_SET_EMPTY_RESPONSE)

    response = await client.get("/api/sets/expand/AS-DEMO-EMPTY")
    assert response.status_code == 200

    expected = []
    assert response.json() == expected


async def test_expand_set_multiple_paths(client, httpserver):
    # AS-DEMO-4 is included through multiple paths, they should all be included
    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    httpserver.expect_request("/graphql").respond_with_json(
        _set_members_response(
            {
                "AS-DEMO-1": {"DEMO": ["AS-DEMO-2", "AS-DEMO-3"]},
                "AS-DEMO-2": {"DEMO": ["AS-DEMO-4"]},
                "AS-DEMO-3": {"DEMO": ["AS-DEMO-4"]},
                "AS-DEMO-4": {"DEMO": ["AS64500"]},
            }
        )
    )

    response = await client.get("/api/sets/expand/AS-DEMO-1")
    assert response.status_code == 200
    assert [(entry["depth"], entry["path"]) for entry in response.json()] == [
        (1, ["AS-DEMO-1"]),
        (2, ["AS-DEMO-1", "AS-DEMO-2"]),
        (2, ["AS-DEMO-1", "AS-DEMO-3"]),
        (3, ["AS-DEMO-1", "AS-DEMO-2", "AS-DEMO-4"]),
        (3, ["AS-DEMO-1", "AS-DEMO-3", "AS-DEMO-4"]),
    ]


async def test_expand_path_limit(client, httpserver, monkeypatch):
    # AS-DEMO-1 and its 20 sub-sets are 21 paths, the limit allows 5
    sub_sets = [f"AS-DEMO-SUB{number}" for number in range(20)]
    sets = {"AS-DEMO-1": {"DEMO": sub_sets}}
    for sub_set in sub_sets:
        sets[sub_set] = {"DEMO": ["AS64500"]}

    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    httpserver.expect_request("/graphql").respond_with_json(_set_members_response(sets))
    monkeypatch.setattr(collectors, "SET_PATH_LIMIT", 5)

    response = await client.get("/api/sets/expand/AS-DEMO-1")
    assert response.status_code == 200
    assert len(response.json()) == 5


async def test_expand_timeout(client, httpserver, monkeypatch):
    def slow_handler(request):
        time.sleep(0.5)
        return Response("{}", content_type="application/json")

    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    httpserver.expect_request("/graphql").respond_with_handler(slow_handler)
    monkeypatch.setattr(queries, "SET_EXPANSION_TIMEOUT", 0.1)

    response = await client.get("/api/sets/expand/AS-DEMO-1")
    assert response.status_code == 504
    assert "timed out" in response.text
