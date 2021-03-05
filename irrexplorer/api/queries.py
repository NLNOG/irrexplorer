import enum
import re
from dataclasses import dataclass
from ipaddress import ip_network

import IPy
from dataclasses_json import LetterCase, dataclass_json
from starlette.responses import PlainTextResponse, JSONResponse

from irrexplorer.api.collectors import PrefixCollector, collect_member_of, collect_set_expansion
from irrexplorer.api.report import enrich_prefix_summaries_with_report
from irrexplorer.api.utils import DataClassJSONResponse

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
            trimmed = raw_query[2:] if raw_query.upper().startswith("AS") else raw_query
            self.cleaned_value = "AS" + str(int(trimmed))
            self.category = QueryCategory.ASN
            return
        except ValueError:
            pass

        try:
            self.cleaned_value = str(IPy.IP(raw_query, make_net=True))
            self.category = QueryCategory.PREFIX
            return
        except ValueError:
            pass

        if re_rpsl_name.match(raw_query):
            self.cleaned_value = raw_query.upper()
            self.category = QueryCategory.ASSET
            return

        raise ValueError("Query is not a valid prefix, IP, ASN or AS-set")


async def clean_query(request):
    try:
        return DataClassJSONResponse(Query(request.path_params["query"]))
    except ValueError as ve:
        return PlainTextResponse(status_code=400, content=str(ve))


async def prefixes_prefix(request):
    try:
        parameter = ip_network(request.path_params["prefix"])
    except ValueError as ve:
        return PlainTextResponse(status_code=400, content=f"Invalid prefix: {ve}")
    summaries = await PrefixCollector(request.app.state.database).prefix_summary(parameter)
    enrich_prefix_summaries_with_report(summaries)
    return DataClassJSONResponse(summaries)


async def prefixes_asn(request):
    asn_prefixes = await PrefixCollector(request.app.state.database).asn_summary(
        request.path_params["asn"]
    )
    enrich_prefix_summaries_with_report(asn_prefixes.direct_origin)
    enrich_prefix_summaries_with_report(asn_prefixes.overlaps)
    return DataClassJSONResponse(asn_prefixes)


async def member_of(request):
    sets = await collect_member_of(request.path_params["target"])
    return DataClassJSONResponse(sets)


async def set_expansion(request):
    result = await collect_set_expansion(request.path_params["target"])
    return DataClassJSONResponse(result)

