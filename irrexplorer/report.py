import asyncio
import time
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from databases import Database

from irrexplorer.backends.bgp import BGPQuery
from irrexplorer.backends.irrd import IRRDQuery
from irrexplorer.backends.rirstats import RIRStatsQuery
from irrexplorer.state import RIR, IPNetwork, PrefixIRRDetail, PrefixSummary, RouteInfo, RPKIStatus


class PrefixReport:
    def __init__(self, database: Database):
        self.database = database
        self.rirstats: List[RouteInfo] = []

    async def prefix_summary(self, search_prefix: IPNetwork):
        start = time.perf_counter()

        bgp_per_prefix, irrd_per_prefix = await self._collect(search_prefix)
        summaries_per_prefix = self._collate_per_prefix(bgp_per_prefix, irrd_per_prefix)
        self._enrich_with_report(summaries_per_prefix)
        print(f"complete in {time.perf_counter()-start}")
        print(summaries_per_prefix)
        return summaries_per_prefix

    async def _collect(
        self, search_prefix: IPNetwork
    ) -> Tuple[Dict[IPNetwork, List[RouteInfo]], Dict[IPNetwork, List[RouteInfo]]]:
        """
        Collect all relevant data for `search_prefix` from remote systems,
        and do preliminary restructuring
        - sets self.rirstats to a list of RouteInfo objects for RIR stats
        - returns a tuple with BGP first, IRRD data second, each in a dict where
          the key is a prefix and the value is a list of routes from that source
          for that prefix
        """

        routes_irrd, routes_bgp, self.rirstats = await asyncio.gather(
            IRRDQuery().query_prefix_any(search_prefix),
            BGPQuery(self.database).query_prefix_any(search_prefix),
            RIRStatsQuery(self.database).query_prefix_any(search_prefix),
        )

        irrd_per_prefix = defaultdict(list)
        for result in routes_irrd:
            irrd_per_prefix[result.prefix].append(result)

        bgp_per_prefix = defaultdict(list)
        for result in routes_bgp:
            bgp_per_prefix[result.prefix].append(result)

        return bgp_per_prefix, irrd_per_prefix

    def _collate_per_prefix(
        self,
        bgp_per_prefix: Dict[IPNetwork, List[RouteInfo]],
        irrd_per_prefix: Dict[IPNetwork, List[RouteInfo]],
    ) -> List[PrefixSummary]:
        """
        Collate the data per prefix into a list of PrefixSummary objects.
        Translates the output from _collect into a list of PrefixSummary objects,
        one per unique prefix found, with the RIR, BGP origins, and IRR routes set.
        """
        all_prefixes = set(irrd_per_prefix.keys()).union(set(bgp_per_prefix.keys()))
        summaries_per_prefix = []
        for prefix in all_prefixes:
            rir = self._rir_for_prefix(prefix)

            bgp_origins = {r.asn for r in bgp_per_prefix.get(prefix, []) if r.asn}
            summary = PrefixSummary(prefix=prefix, rir=rir, bgp_origins=bgp_origins)

            if prefix in irrd_per_prefix:
                irr_entries = irrd_per_prefix[prefix]
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

    def _enrich_with_report(self, summaries_per_prefix):
        for s in summaries_per_prefix:
            # Detect superfluous route objects
            if not s.bgp_origins and s.irr_origins:
                s.info("Route objects exist, but prefix not seen in DFZ")
            if not s.bgp_origins and s.rpki_origins:
                s.info("RPKI ROA exists, but prefix not seen in DFZ")

            # Detect route objects in unexpected IRR and check origin
            if s.irr_expected_rir and s.irr_routes and not s.irr_routes_expected_rir:
                s.warning(
                    f"Expected route object in {s.irr_expected_rir}, but only found in other IRRs"
                )
            elif s.irr_expected_rir and s.irr_origins_not_expected_rir:
                s.info(
                    f"Expected route object in {s.irr_expected_rir}, "
                    f"but objects also exist in other IRRs"
                )

            if s.bgp_origins - s.irr_origins:
                s.danger("No route objects match DFZ origin")
            elif s.irr_routes_expected_rir and s.bgp_origins - s.irr_origins_expected_rir:
                s.danger(
                    f"Expected route object in {s.irr_expected_rir}, but BGP origin does not "
                    f"match. Objects from other IRRs do match BGP origin"
                )
            elif s.irr_origins_not_expected_rir and s.bgp_origins - s.irr_origins_not_expected_rir:
                s.danger(
                    f"Expected route object in {s.irr_expected_rir} matches BGP origin, "
                    f"but non-matching objects exist in other IRRs"
                )
            elif len(s.irr_origins) > 1:
                s.warning("Multiple route objects exist with different origins")

            # Detect RPKI situation
            if not s.rpki_origins:
                s.info("No RPKI ROA found for prefix")
            else:
                if s.bgp_origins - s.rpki_origins:
                    s.danger("RPKI origin does not match BGP origin")
                elif [r for r in s.irr_routes_all if r.rpki_status == RPKIStatus.invalid]:
                    s.warning("RPKI invalid route objects found")

            s.finalise_status()

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
