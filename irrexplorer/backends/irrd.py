import asyncio
from ipaddress import ip_network
from typing import List

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

from irrexplorer.settings import config
from irrexplorer.state import DataSource, IPNetwork, RouteInfo, RPKIStatus

IRRD_TIMEOUT = 600

COMMON_GRAPHQL_FIELDS = """
    rpslPk
    objectClass
    source
    ... on RPSLRoute {
      prefix
      asn
      rpkiStatus
      rpkiMaxLength
    }
    ... on RPSLRoute6 {
      prefix
      asn
      rpkiStatus
      rpkiMaxLength
    }
"""

GQL_QUERY_ASN = gql(
    f"""
    query getRoutes ($asn: [ASN!]) {{
        rpslObjects(
            asn: $asn
            objectClass: ["route", "route6"],
            rpkiStatus: [valid,invalid,not_found]
        ) {{
            {COMMON_GRAPHQL_FIELDS}
        }}
    }}
"""
)

GQL_QUERY_PREFIX = gql(
    f"""
    query getRoutes ($prefix: IP!, $object_class: [String!]!) {{
        rpslObjects(
            ipAny: $prefix
            objectClass: $object_class,
            rpkiStatus: [valid,invalid,not_found]
        ) {{
            {COMMON_GRAPHQL_FIELDS}
        }}
    }}
"""
)


class IRRDQuery:
    def __init__(self):
        # Read at this point to allow tests to change the endpoint
        endpoint = config("IRRD_ENDPOINT")
        self.transport = AIOHTTPTransport(url=endpoint, timeout=IRRD_TIMEOUT)

    async def query_asn(self, asn: int):
        async with Client(transport=self.transport, execute_timeout=IRRD_TIMEOUT) as session:
            result = await session.execute(GQL_QUERY_ASN, {"asn": asn})
            return self._graphql_to_route_info(result)

    async def query_prefixes_any(self, prefixes: List[IPNetwork]) -> List[RouteInfo]:
        tasks = []
        async with Client(transport=self.transport, execute_timeout=IRRD_TIMEOUT) as session:
            for prefix in prefixes:
                object_class = ["route"] if prefix.version == 4 else ["route6"]
                task = session.execute(
                    GQL_QUERY_PREFIX,
                    {
                        "prefix": str(prefix),
                        "object_class": object_class,
                    },
                )
                tasks.append(task)
            results_lists = await asyncio.gather(*tasks)
            objects_lists = [
                self._graphql_to_route_info(results_list) for results_list in results_lists
            ]
        return [obj for objects_list in objects_lists for obj in objects_list]

    def _graphql_to_route_info(self, graphql_result) -> List[RouteInfo]:
        """
        Convert the response to an IRRd rpslObjects query
        to a list of RouteInfo objects.
        """
        results = []
        for rpsl_obj in graphql_result["rpslObjects"]:
            results.append(
                RouteInfo(
                    source=DataSource.IRR,
                    prefix=ip_network(rpsl_obj["prefix"]),
                    asn=rpsl_obj["asn"] if rpsl_obj["asn"] else 0,  # TODO: fix in irrd
                    rpsl_pk=rpsl_obj["rpslPk"],
                    irr_source=rpsl_obj["source"],
                    rpki_status=RPKIStatus[rpsl_obj["rpkiStatus"]],
                    rpki_max_length=rpsl_obj["rpkiMaxLength"],
                )
            )

        return results
