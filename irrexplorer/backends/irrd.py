from ipaddress import ip_network
from typing import List

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

from irrexplorer.config import IRRD_ENDPOINT
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
        # TODO: Common client?
        self.transport = AIOHTTPTransport(url=IRRD_ENDPOINT, timeout=IRRD_TIMEOUT)
        self.client = Client(
            transport=self.transport,
            fetch_schema_from_transport=True,
            execute_timeout=IRRD_TIMEOUT,
        )

    async def query_asn(self, asn: int):
        result = await self.client.execute_async(GQL_QUERY_ASN, {"asn": asn})
        return self._graphql_to_route_info(result)

    async def query_prefix_any(self, prefix: IPNetwork) -> List[RouteInfo]:
        object_class = ["route"] if prefix.version == 4 else ["route6"]
        result = await self.client.execute_async(
            GQL_QUERY_PREFIX,
            {
                "prefix": str(prefix),
                "object_class": object_class,
            },
        )
        return self._graphql_to_route_info(result)

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
