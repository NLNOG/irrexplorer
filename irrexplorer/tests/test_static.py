import pytest

pytestmark = pytest.mark.asyncio


async def test_index(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert '<div id="root">' in response.text


async def test_media(client):
    response = await client.get("/robots.txt")
    assert response.status_code == 200
    assert "Disallow" in response.text


async def test_default(client):
    response = await client.get("/prefix/foo")
    assert response.status_code == 200
    assert '<div id="root">' in response.text


async def test_not_found(client):
    response = await client.get("/not-found")
    assert response.status_code == 404
