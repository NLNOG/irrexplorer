import contextlib
import os
import signal
import sys
import threading
import traceback

import databases
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount, Route

from irrexplorer.api import queries
from irrexplorer.api.utils import DefaultIndexStaticFiles
from irrexplorer.settings import DATABASE_URL, DEBUG, TESTING


@contextlib.asynccontextmanager
async def lifespan(app):
    signal.signal(signal.SIGUSR1, sigusr1_handler)
    app.state.database = databases.Database(DATABASE_URL, force_rollback=TESTING)
    await app.state.database.connect()
    yield
    await app.state.database.disconnect()


routes = [
    Route("/api/metadata/", queries.metadata),
    Route("/api/clean_query/{query:path}", queries.clean_query),
    Route("/api/prefixes/asn/AS{asn:int}", queries.prefixes_asn),
    Route("/api/prefixes/asn/{asn:int}", queries.prefixes_asn),
    Route("/api/prefixes/prefix/{prefix:path}", queries.prefixes_prefix),
    Route("/api/sets/member-of/{object_class}/{target}", queries.member_of),
    # legacy endpoint before object class was added:
    Route("/api/sets/member-of/{target}", queries.member_of),
    Route("/api/sets/expand/{target}", queries.set_expansion),
    Mount(
        "/",
        DefaultIndexStaticFiles(
            directory="frontend/build",
            html=True,
            defaulted_paths=["prefix/", "asn/", "as-set/", "status"],
        ),
    ),
]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_headers=["Cache-Control", "Pragma", "Expires"],
    )
]

app = Starlette(
    debug=DEBUG,
    routes=routes,
    middleware=middleware,
    lifespan=lifespan,
)


def sigusr1_handler(signal, frame):  # pragma: no cover
    thread_names = {th.ident: th.name for th in threading.enumerate()}
    code = [f"Traceback follows for all threads of process {os.getpid()}:"]
    for thread_id, stack in sys._current_frames().items():
        thread_name = thread_names.get(thread_id, "")
        code.append(f"\n## Thread: {thread_name}({thread_id}) ##\n")
        code += traceback.format_list(traceback.extract_stack(stack))
    print("".join(code))
