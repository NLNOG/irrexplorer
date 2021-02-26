import asyncio
import time
from collections import defaultdict
from typing import Dict, List, Optional

from databases import Database

from irrexplorer.api.interfaces import PrefixIRRDetail, PrefixSummary
from irrexplorer.backends.bgp import BGPQuery
from irrexplorer.backends.irrd import IRRDQuery
from irrexplorer.backends.rirstats import RIRStatsQuery
from irrexplorer.settings import TESTING
from irrexplorer.state import RIR, IPNetwork, RouteInfo


class PrefixCollector:
    """
    Collect data about a particular prefix.

    Given a search prefix, call prefix_summary() to get a list
    of PrefixSummary objects, each of which contains all the info
    about one prefix.
    """

    def __init__(self, database: Database):
        self.database = database
        self.rirstats: List[RouteInfo] = []
        self.routes_irrd: Dict[IPNetwork, List[RouteInfo]] = {}
        self.routes_bgp: Dict[IPNetwork, List[RouteInfo]] = {}

    async def prefix_summary(self, search_prefix: IPNetwork) -> List[PrefixSummary]:
        start = time.perf_counter()

        await self._collect(search_prefix)
        prefix_summaries = self._collate_per_prefix()
        print(f"complete in {time.perf_counter()-start}")
        print(prefix_summaries)
        return prefix_summaries

    async def _collect(self, search_prefix: IPNetwork) -> None:
        """
        Collect all relevant data for `search_prefix` from remote systems,
        and set the results into self.irrd_per_prefix,
        self.bgp_per_prefix and self.rirstats.
        """
        tasks = [
            IRRDQuery().query_prefix_any(search_prefix),
            BGPQuery(self.database).query_prefix_any(search_prefix),
            RIRStatsQuery(self.database).query_prefix_any(search_prefix),
        ]
        # force_rollback, used in tests, has issues with executing the tasks
        # concurrently - therefore, in testing, they're executed sequentially
        if TESTING:
            routes_irrd, routes_bgp, self.rirstats = [await t for t in tasks]
        else:  # pragma: no cover
            routes_irrd, routes_bgp, self.rirstats = await asyncio.gather(*tasks)

        self.irrd_per_prefix = defaultdict(list)
        for result in routes_irrd:
            self.irrd_per_prefix[result.prefix].append(result)

        self.bgp_per_prefix = defaultdict(list)
        for result in routes_bgp:
            self.bgp_per_prefix[result.prefix].append(result)

    def _collate_per_prefix(self) -> List[PrefixSummary]:
        """
        Collate the data per prefix into a list of PrefixSummary objects.
        Translates the output from _collect into a list of PrefixSummary objects,
        one per unique prefix found, with the RIR, BGP origins, and IRR routes set.
        """
        all_prefixes = set(self.irrd_per_prefix.keys()).union(set(self.bgp_per_prefix.keys()))
        summaries_per_prefix = []
        for prefix in all_prefixes:
            rir = self._rir_for_prefix(prefix)

            bgp_origins = {r.asn for r in self.bgp_per_prefix.get(prefix, []) if r.asn}
            summary = PrefixSummary(prefix=prefix, rir=rir, bgp_origins=bgp_origins)

            if prefix in self.irrd_per_prefix:
                irr_entries = self.irrd_per_prefix[prefix]
                irr_entries.sort(key=lambda r: r.asn if r.asn else 0)
                for entry in irr_entries:
                    assert entry.asn is not None, entry
                    assert entry.irr_source, entry
                    if entry.irr_source == "RPKI":
                        target = summary.rpki_routes
                    else:
                        target = summary.irr_routes[entry.irr_source]
                    target.append(
                        PrefixIRRDetail(
                            asn=entry.asn,
                            rpsl_pk=entry.rpsl_pk,
                            rpki_status=entry.rpki_status,
                        )
                    )
            summaries_per_prefix.append(summary)
        return summaries_per_prefix

    def _rir_for_prefix(self, prefix: IPNetwork) -> Optional[RIR]:
        """
        Find the responsible RIR for a prefix, from self.rirstats previously
        gathered by _collect()
        """
        relevant_rirstats = (
            rirstat for rirstat in self.rirstats if rirstat.prefix.overlaps(prefix)  # type: ignore
        )
        try:
            return next(relevant_rirstats).rir
        except StopIteration:
            return None
