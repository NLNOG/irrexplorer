from os import environ

import pytest

pytestmark = pytest.mark.asyncio

IRRD_SET_EMPTY_RESPONSE = {"data": {"recursiveSetMembers": [{"rpslPk": "AS-DEMO-EMPTY", "members": []}]}}  # type: ignore

IRRD_SET_VALID_RESPONSE = {
    "data": {
        "recursiveSetMembers": [
            {
                "rpslPk": "AS-DEMO-1",
                "members": [
                    "AS64500",
                    "AS-DEMO-2",
                ],
            },
            {
                "rpslPk": "AS-DEMO-2",
                "members": [
                    "AS-DEMO-3",
                    "AS64501",
                ],
            },
            {
                "rpslPk": "AS-DEMO-3",
                "members": [
                    "AS-DEMO-4",
                    "AS-DEMO-1",
                    "AS64502",
                ],
            },
        ]
    },
}

IRRD_DEEP_RESPONSE_MEMBERS = ["AS64500"] + [f"AS-DEMO-{i}" for i in range(2000)]
IRRD_SET_DEEP_RESPONSE = {
    "data": {
        "recursiveSetMembers": [
            {"rpslPk": "AS-DEMO-1", "members": IRRD_DEEP_RESPONSE_MEMBERS},
            {
                "rpslPk": "AS-DEMO-2",
                "members": [
                    "AS64501",
                ],
            },
        ]
    },
}


async def test_expand_valid(client, httpserver):
    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    httpserver.expect_request("/graphql").respond_with_json(IRRD_SET_VALID_RESPONSE)

    response = await client.get("/api/sets/expand/AS-DEMO-1")
    assert response.status_code == 200
    expected = [
        {
            "name": "AS-DEMO-1",
            "depth": 1,
            "path": ["AS-DEMO-1"],
            "members": ["AS-DEMO-2", "AS64500"],
        },
        {
            "name": "AS-DEMO-2",
            "depth": 2,
            "path": ["AS-DEMO-1", "AS-DEMO-2"],
            "members": ["AS-DEMO-3", "AS64501"],
        },
        {
            "name": "AS-DEMO-3",
            "depth": 3,
            "path": ["AS-DEMO-1", "AS-DEMO-2", "AS-DEMO-3"],
            "members": ["AS-DEMO-1", "AS-DEMO-4", "AS64502"],
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
        "path": ["AS-DEMO-1", "AS-DEMO-2"],
        "members": ["AS64501"],
    }


async def test_expand_no_data(client, httpserver):
    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    httpserver.expect_request("/graphql").respond_with_json(IRRD_SET_EMPTY_RESPONSE)

    response = await client.get("/api/sets/expand/AS-DEMO-EMPTY")
    assert response.status_code == 200

    expected = [{"members": [], "name": "AS-DEMO-EMPTY", "depth": 1, "path": ["AS-DEMO-EMPTY"]}]
    assert response.json() == expected
