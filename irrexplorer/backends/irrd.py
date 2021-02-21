import asyncio

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

from irrexplorer.config import IRRD_ENDPOINT


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
    query_asn = gql(f"""
        query getRoutes ($asn: [ASN!]) {{
            rpslObjects(
                asn: $asn
                objectClass: ["route", "route6"],
                rpkiStatus: [valid,invalid,not_found]
            ) {{
                {graphql_fields}
            }}
        }}
    """)

    def __init__(self):
        self.transport = AIOHTTPTransport(url=IRRD_ENDPOINT)

    async def routes(self, asn: int):
        async with Client(transport=self.transport, fetch_schema_from_transport=True) as session:
            result = await session.execute(self.query_asn, {"asn": asn})
            print(result)


asyncio.run(IRRDQuery().routes(213279))
