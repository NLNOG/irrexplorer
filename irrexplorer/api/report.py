from typing import List

from irrexplorer.api.interfaces import PrefixSummary
from irrexplorer.settings import SPECIAL_USE_SPACE
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

        if not s.rpki_origins and ["0"]:
            if not s.bgp_origins and s.rpki_origins:
                s.info("RPKI ROA exists, but prefix not seen in DFZ")

        # Detect route objects in unexpected IRR
        if s.irr_expected_rir and s.irr_routes and not s.irr_routes_expected_rir:
            s.warning(
                f"Expected route object in {s.irr_expected_rir}, but only found in other IRRs"
            )

        # Check route objects against origins
        if s.bgp_origins - s.irr_origins:
            s.danger("No route objects match DFZ origin")
        elif s.irr_routes_expected_rir and s.bgp_origins - s.irr_origins_expected_rir:
            s.danger(
                f"Expected route object in {s.irr_expected_rir}, but BGP origin does not "
                f"match. Objects from other IRRs do match BGP origin"
            )
        elif s.irr_origins_not_expected_rir and s.bgp_origins - s.irr_origins_not_expected_rir:
            s.warning(
                f"Expected route object in {s.irr_expected_rir} matches BGP origin, "
                f"but non-matching objects exist in other IRRs"
            )
        elif len(s.irr_origins) > 1:
            s.warning("Multiple route objects exist with different origins")

        # Detect RPKI situation
        if s.rpki_origins and s.bgp_origins - s.rpki_origins:
            s.danger("RPKI origin does not match BGP origin")
        if any([r.rpki_status == RPKIStatus.invalid for r in s.irr_routes_all]):
            s.danger("RPKI invalid route objects found")
        elif s.irr_routes and all(
            [r.rpki_status == RPKIStatus.not_found for r in s.irr_routes_all]
        ):
            s.info("No (covering) RPKI ROA found for route objects")

        for name, special_use_prefix in SPECIAL_USE_SPACE:
            if s.prefix.overlaps(special_use_prefix):
                s.danger(f"Overlaps with {name} special use prefix {special_use_prefix}")

        s.finalise_status()
