from ipaddress import ip_network

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

from irrexplorer.config import IRRD_ENDPOINT
from irrexplorer.state import DataSource, RouteInfo, RPKIStatus


class IRRDQuery:
    graphql_fields = """
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
    gql_query_asn = gql(
        f"""
        query getRoutes ($asn: [ASN!]) {{
            rpslObjects(
                asn: $asn
                objectClass: ["route", "route6"],
                rpkiStatus: [valid,invalid,not_found]
            ) {{
                {graphql_fields}
            }}
        }}
    """
    )
    gql_query_prefix = gql(
        f"""
        query getRoutes ($prefix: IP!, $object_class: [String!]!) {{
            rpslObjects(
                ipAny: $prefix
                objectClass: $object_class,
                rpkiStatus: [valid,invalid,not_found]
            ) {{
                {graphql_fields}
            }}
        }}
    """
    )

    def __init__(self):
        self.transport = AIOHTTPTransport(url=IRRD_ENDPOINT, timeout=600)
        self.client = Client(
            transport=self.transport,
            fetch_schema_from_transport=True,
            execute_timeout=600,
        )
        print("created client IRRd")

    async def query_asn(self, asn: int):
        async with Client(transport=self.transport, fetch_schema_from_transport=True) as session:
            result = await session.execute(self.query_asn, {"asn": asn})
            print(result)

    async def query_routes(self, ip_version: int, prefix: str):
        results = []
        object_class = ["route"] if ip_version == 4 else ["route6"]
        print("running IRRd")
        result = await self.client.execute_async(
            self.gql_query_prefix,
            {
                "prefix": prefix,
                "object_class": object_class,
            },
        )
        for rpsl_obj in result["rpslObjects"]:
            results.append(
                RouteInfo(
                    source=DataSource.IRR,
                    prefix=ip_network(rpsl_obj["prefix"]),
                    asn=rpsl_obj["asn"],
                    rpsl_pk=rpsl_obj["rpslPk"],
                    irr_source=rpsl_obj["source"],
                    rpki_status=RPKIStatus[rpsl_obj["rpkiStatus"]],
                    rpki_max_length=rpsl_obj["rpkiMaxLength"],
                )
            )

        print("finish IRRd")
        return results
