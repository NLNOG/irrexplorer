from typing import List

from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.staticfiles import StaticFiles


class DataClassJSONResponse(Response):
    media_type = "application/json"

    def render(self, content) -> bytes:
        if isinstance(content, list):
            if not content:  # pragma: no cover - we don't actually use this
                return b"[]"
            return content[0].schema().dumps(content, many=True).encode("utf-8")
        if not content:  # pragma: no cover
            return b"null"
        return content.schema().dumps(content).encode("utf-8")


class DefaultIndexStaticFiles(StaticFiles):
    """
    Patched version of StaticFiles that routes any request starting
    with any defaulted_paths entry, that does not map to a file, to
    a request for index.html.
    The frontend rewrites the URL for each query, and this is needed
    to still map those urls, like /asn/AS3333, to index.html.
    """

    defaulted_paths: List[str] = []

    def __init__(self, defaulted_paths=None, *args, **kwargs):
        if defaulted_paths:
            self.defaulted_paths = defaulted_paths

        super().__init__(*args, **kwargs)

    async def get_response(self, path: str, *args, **kwargs) -> Response:
        try:
            response = await super().get_response(path, *args, **kwargs)
        except HTTPException as exc:
            if exc.status_code == 404 and any([path.startswith(p) for p in self.defaulted_paths]):
                return await super().get_response("index.html", *args, **kwargs)
            raise
        return response
