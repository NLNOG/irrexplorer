import asyncio
import time
from collections import defaultdict

from irrexplorer.backends.bgp import BGPQuery
from irrexplorer.backends.irrd import IRRDQuery
from irrexplorer.backends.rirstats import RIRStatsQuery
from irrexplorer.state import PrefixSourceDetail, PrefixSummary


async def main():
    ip_version = 4
    prefix = "193.0.0.0/20"
    irrd_query = IRRDQuery()
    print("running!")
    start = time.perf_counter()
    results_nested = await asyncio.gather(
        RIRStatsQuery().query_prefix(ip_version, prefix),
        irrd_query.query_routes(ip_version, prefix),
        BGPQuery().query_prefix(ip_version, prefix),
    )
    rirstats, others = results_nested[0], results_nested[1:]
    results = [item for sublist in others for item in sublist]
    gathered = defaultdict(list)
    for result in results:
        gathered[result.prefix].append(result)

    summaries = []
    for prefix, entries in gathered.items():
        details = []
        for entry in entries:
            details.append(
                PrefixSourceDetail(
                    source=entry.source,
                    asn=entry.asn,
                    irr_source=entry.irr_source,
                    rpsl_pk=entry.rpsl_pk,
                )
            )
        summaries.append(
            PrefixSummary(
                prefix=prefix,
                details=details,
                rir=rirstats[0].rir,  # TODO: breaks for zero or multiple RIRstats
            )
        )

    for summary in summaries:
        print(summary)
    print(f"complete in {time.perf_counter()-start}")
    # async for p in tasks:
    # async for bgp in :
    #     print(bgp)
    #
    # async for rpsl in :
    #     print(rpsl)


asyncio.run(main())
