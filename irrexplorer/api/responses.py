from starlette.responses import Response


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
