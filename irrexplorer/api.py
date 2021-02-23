import enum
import re
from dataclasses import dataclass
from ipaddress import ip_network

from dataclasses_json import dataclass_json, LetterCase
from starlette.responses import PlainTextResponse, Response, JSONResponse
import IPy

from irrexplorer import report

re_rpsl_name = re.compile(r"^[A-Z][A-Z0-9_:-]*[A-Z0-9]$", re.IGNORECASE)


class QueryCategory(enum.Enum):
    ASN = "asn"
    PREFIX = "prefix"
    ASSET = "as-set"


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Query:
    category: QueryCategory
    cleaned_value: str

    def __init__(self, raw_query: str):
        raw_query = raw_query.strip()

        try:
            self.cleaned_value = str(IPy.IP(raw_query, make_net=True))
            self.category = QueryCategory.PREFIX
            return
        except ValueError:
            pass

        try:
            trimmed = raw_query[2:] if raw_query.startswith('AS') else raw_query
            self.cleaned_value = 'AS' + str(int(trimmed))
            self.category = QueryCategory.ASN
            return
        except ValueError:
            pass

        if re_rpsl_name.match(raw_query):
            self.cleaned_value = raw_query.upper()
            self.category = QueryCategory.ASSET
            return

        raise ValueError('Query is not a valid prefix, IP, ASN or AS-set')


async def clean_query(request):
    try:
        return DataClassJSONResponse(Query(request.path_params['query']))
    except ValueError as ve:
        return PlainTextResponse(status_code=400, content=str(ve))


async def prefix(request):
    try:
        parameter = ip_network(request.path_params["prefix"])
    except ValueError as ve:
        return PlainTextResponse(status_code=400, content=f"Invalid prefix: {ve}")
    result = await report.PrefixReport(request.app.state.database).prefix_summary(parameter)
    return DataClassJSONResponse(result)


class DataClassJSONResponse(Response):
    media_type = "application/json"

    def render(self, content) -> bytes:
        if isinstance(content, list):
            if not content:
                return b'[]'
            return content[0].schema().dumps(content, many=True).encode("utf-8")
        if not content:
            return b'null'
        return content.schema().dumps(content).encode("utf-8")
