from datetime import datetime, timezone
from os import environ

import pytest

from irrexplorer.backends.metadata import update_last_data_import

pytestmark = pytest.mark.asyncio

IRRD_LAST_UPDATE_RESPONSE = {
    "data": {
        "databaseStatus": [
            {"source": "DEMO", "lastUpdate": "2023-01-01T00:00:00.000000+00:00"},
        ]
    },
}


async def test_metadata_last_update(client, httpserver):
    environ["IRRD_ENDPOINT"] = httpserver.url_for("/graphql")
    httpserver.expect_request("/graphql").respond_with_json(IRRD_LAST_UPDATE_RESPONSE)
    await update_last_data_import(datetime(2023, 1, 2, tzinfo=timezone.utc))

    response = await client.get("/api/metadata/")
    assert response.status_code == 200
    expected = {
        "last_update": {
            "irr": {"DEMO": "2023-01-01 00:00:00+00:00"},
            "importer": "2023-01-02 00:00:00+00:00",
        }
    }
    assert response.json() == expected
