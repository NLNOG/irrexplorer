import pytest

pytestmark = pytest.mark.asyncio


async def test_clean_query_prefix(client):
    response = await client.get("/api/clean_query/192.0.2/24")
    assert response.status_code == 200
    assert response.json() == {"cleanedValue": "192.0.2.0/24", "category": "prefix"}


async def test_clean_query_prefix_misaligned(client):
    response = await client.get("/api/clean_query/192.0.2.3/24")
    assert response.status_code == 200
    assert response.json() == {"cleanedValue": "192.0.2.0/24", "category": "prefix"}


async def test_clean_query_asn_bare(client):
    response = await client.get("/api/clean_query/192")
    assert response.status_code == 200
    assert response.json() == {"cleanedValue": "AS192", "category": "asn"}


async def test_clean_query_asn(client):
    response = await client.get("/api/clean_query/AS64500")
    assert response.status_code == 200
    assert response.json() == {"cleanedValue": "AS64500", "category": "asn"}


async def test_clean_query_as_set(client):
    response = await client.get("/api/clean_query/foobar")
    assert response.status_code == 200
    assert response.json() == {"cleanedValue": "FOOBAR", "category": "as-set"}


async def test_clean_query_invalid(client):
    response = await client.get("/api/clean_query/--invalid-💩")
    assert response.status_code == 400
