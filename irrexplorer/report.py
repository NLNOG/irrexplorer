from typing import List

from irrexplorer.api.interfaces import PrefixSummary
from irrexplorer.state import RPKIStatus


def enrich_prefix_summaries_with_report(prefix_summaries: List[PrefixSummary]):
    """
    Given a list of PrefixSummary objects, enriches them with reporting info.
    This fills the messages attribute by calling the info/warning/danger methods.
    To help, PrefixSummary has quite a few properties for simpler access to data,
    which are extensively used.
    """
    for s in prefix_summaries:
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
