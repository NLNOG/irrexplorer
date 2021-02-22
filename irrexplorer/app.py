import typing
from ipaddress import ip_network

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from irrexplorer import api


async def prefix(request):
    try:
        parameter = ip_network(request.path_params['prefix'])
    except ValueError as ve:
        return PlainTextResponse(status_code=400, content=f'Invalid prefix: {ve}')
    result = await api.prefix(parameter)
    return DataClassJSONResponse(result)


class DataClassJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return content[0].schema().dumps(content, many=True).encode('utf-8')


def startup():
    print("Ready to go")


routes = [
    Route("/api/prefix/{prefix:path}", prefix),
    Mount("/", StaticFiles(directory="frontend/build", html=True)),
]

middleware = [
    Middleware(CORSMiddleware, allow_origins=['*'])
]

app = Starlette(debug=True, routes=routes, middleware=middleware, on_startup=[startup])
