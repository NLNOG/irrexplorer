import asyncio
import time
from collections import defaultdict

from databases import Database

from irrexplorer.backends.bgp import BGPQuery
from irrexplorer.backends.irrd import IRRDQuery
from irrexplorer.backends.rirstats import RIRStatsQuery
from irrexplorer.state import IPNetwork, PrefixIRRDetail, PrefixSummary


async def prefix_summary(database: Database, search_prefix: IPNetwork):
    start = time.perf_counter()

    routes_irrd, rirstats, routes_bgp = await asyncio.gather(
        IRRDQuery().query_prefix_any(search_prefix),
        RIRStatsQuery(database).query_prefix_any(search_prefix),
        BGPQuery(database).query_prefix_any(search_prefix),
    )

    irrd_per_prefix = defaultdict(list)
    for result in routes_irrd:
        irrd_per_prefix[result.prefix].append(result)

    bgp_per_prefix = defaultdict(list)
    for result in routes_bgp:
        bgp_per_prefix[result.prefix].append(result)

    all_prefixes = set(irrd_per_prefix.keys()).union(set(bgp_per_prefix.keys()))
    summaries_per_prefix = []
    for prefix in all_prefixes:
        relevant_rirstats = (
            rirstat for rirstat in rirstats if rirstat.prefix.overlaps(search_prefix)
        )
        rir = next(relevant_rirstats).rir

        bgp_origins = {r.asn for r in bgp_per_prefix.get(prefix, []) if r.asn}
        summary = PrefixSummary(prefix=prefix, rir=rir, bgp_origins=bgp_origins)

        if prefix in irrd_per_prefix:
            irr_entries = irrd_per_prefix[prefix]
            # Sort IRR alphabetically, but always with RPKI first
            irr_entries.sort(key=lambda e: e.irr_source if e.irr_source else '')
            irr_entries.sort(key=lambda e: e.irr_source != "RPKI")
            for entry in irr_entries:
                assert entry.asn is not None, entry
                assert entry.irr_source, entry
                summary.irr_routes[entry.irr_source].append(
                    PrefixIRRDetail(
                        asn=entry.asn,
                        rpsl_pk=entry.rpsl_pk,
                        rpki_status=entry.rpki_status,
                    )
                )
        summaries_per_prefix.append(summary)

    print(f"complete in {time.perf_counter()-start}")
    print(summaries_per_prefix)
    return summaries_per_prefix
