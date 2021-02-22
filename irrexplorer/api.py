import asyncio
import time
from collections import defaultdict
from ipaddress import IPv6Network, IPv4Network
from typing import Union

from irrexplorer.backends.bgp import BGPQuery
from irrexplorer.backends.irrd import IRRDQuery
from irrexplorer.backends.rirstats import RIRStatsQuery
from irrexplorer.state import PrefixSourceDetail, PrefixSummary, IPNetwork


async def prefix(prefix: IPNetwork):
    irrd_query = IRRDQuery()
    print("running!")
    start = time.perf_counter()
    results_nested = await asyncio.gather(
        RIRStatsQuery().query_prefix(prefix),
        irrd_query.query_routes(prefix),
        BGPQuery().query_prefix(prefix),
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
                    rpki_status=entry.rpki_status,
                )
            )
        relevant_rirstats = (rirstat for rirstat in rirstats if rirstat.prefix.overlaps(prefix))
        rir = next(relevant_rirstats).rir
        summaries.append(
            PrefixSummary(
                prefix=prefix,
                details=details,
                rir=rir,
            )
        )

    print(f"complete in {time.perf_counter()-start}")
    return summaries
    # async for p in tasks:
    # async for bgp in :
    #     print(bgp)
    #
    # async for rpsl in :
    #     print(rpsl)
