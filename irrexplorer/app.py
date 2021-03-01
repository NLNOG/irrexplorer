import databases
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount, Route

from irrexplorer.api import queries
from irrexplorer.api.utils import DefaultIndexStaticFiles
from irrexplorer.settings import DATABASE_URL, DEBUG, TESTING


async def startup():
    app.state.database = databases.Database(DATABASE_URL, force_rollback=TESTING)
    await app.state.database.connect()


async def shutdown():
    await app.state.database.disconnect()


routes = [
    Route("/api/clean_query/{query:path}", queries.clean_query),
    Route("/api/prefixes/asn/AS{asn:int}", queries.asn),
    Route("/api/prefixes/asn/{asn:int}", queries.asn),
    Route("/api/prefixes/prefix/{prefix:path}", queries.prefix),
    Mount(
        "/",
        DefaultIndexStaticFiles(
            directory="frontend/build",
            html=True,
            defaulted_paths=["prefix/", "asn/", "as-set/"],
        ),
    ),
]

middleware = [
    Middleware(
        CORSMiddleware, allow_origins=["*"], allow_headers=["Cache-Control", "Pragma", "Expires"]
    )
]

app = Starlette(
    debug=DEBUG,
    routes=routes,
    middleware=middleware,
    on_startup=[startup],
    on_shutdown=[shutdown],
)
