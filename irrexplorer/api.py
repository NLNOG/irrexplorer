import asyncio
import time
from collections import defaultdict
from ipaddress import IPv6Network, IPv4Network
from typing import Union

from irrexplorer.backends.bgp import BGPQuery
from irrexplorer.backends.irrd import IRRDQuery
from irrexplorer.backends.rirstats import RIRStatsQuery
from irrexplorer.state import PrefixIRRDetail, PrefixSummary, IPNetwork, DataSource


async def prefix(search_prefix: IPNetwork):
    irrd_query = IRRDQuery()
    print("running!")
    start = time.perf_counter()
    results_nested = await asyncio.gather(
        RIRStatsQuery().query_prefix(search_prefix),
        irrd_query.query_routes(search_prefix),
        BGPQuery().query_prefix(search_prefix),
    )
    rirstats, others = results_nested[0], results_nested[1:]
    results = [item for sublist in others for item in sublist]
    gathered = defaultdict(list)
    for result in results:
        gathered[result.prefix].append(result)

    summaries = []
    for found_prefix, entries in gathered.items():
        relevant_rirstats = (rirstat for rirstat in rirstats if rirstat.prefix.overlaps(search_prefix))
        rir = next(relevant_rirstats).rir
        bgp_origins = {e.asn for e in entries if e.source == DataSource.BGP}
        summary = PrefixSummary(prefix=found_prefix, rir=rir, bgp_origins=bgp_origins)
        irr_entries = [e for e in entries if e.source == DataSource.IRR]
        irr_entries.sort(key=lambda e: e.irr_source)
        irr_entries.sort(key=lambda e: e.irr_source != 'RPKI')
        for entry in irr_entries:
            summary.irr_routes[entry.irr_source].append(
                PrefixIRRDetail(
                    asn=entry.asn,
                    rpsl_pk=entry.rpsl_pk,
                    rpki_status=entry.rpki_status,
                )
            )
        summaries.append(summary)

    print(f"complete in {time.perf_counter()-start}")
    print(summaries)
    return summaries
    # async for p in tasks:
    # async for bgp in :
    #     print(bgp)
    #
    # async for rpsl in :
    #     print(rpsl)
