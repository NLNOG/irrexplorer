import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists, drop_database
from starlette.config import environ

# Must be set before settings is imported
environ["TESTING"] = "TRUE"

from irrexplorer import settings
from irrexplorer.app import app
from irrexplorer.storage.tables import metadata


@pytest.fixture(autouse=True, scope="session")
def setup_test_database():
    url = str(settings.DATABASE_URL)
    engine = create_engine(url)
    assert not database_exists(url), "Test database already exists. Aborting tests."
    create_database(url)
    metadata.create_all(engine)  # TODO: run migrations
    yield
    drop_database(url)


@pytest.fixture()
async def client():
    # httpx client does not trigger lifespan events on it's own
    # https://github.com/encode/httpx/issues/350
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://testserver") as test_client:
            test_client.app = app
            yield test_client
