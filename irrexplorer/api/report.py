from typing import List

from irrexplorer.api.interfaces import PrefixSummary
from irrexplorer.api.messages import MessageType
from irrexplorer.settings import SPECIAL_USE_SPACE
from irrexplorer.state import RPKIStatus


def enrich_prefix_summaries_with_report(prefix_summaries: List[PrefixSummary]):
    """
    Given a list of PrefixSummary objects, enriches them with reporting info.
    This fills the messages attribute by calling add_message().

    To help, PrefixSummary has quite a few properties for simpler access to data,
    which are extensively used.
    """
    for s in prefix_summaries:
        # Detect superfluous route objects
        if not s.bgp_origins and s.irr_origins:
            s.add_message(MessageType.ROUTE_OBJECTS_NOT_IN_DFZ)
        if not s.bgp_origins and s.rpki_origins and s.rpki_origins != {0}:
            s.add_message(MessageType.RPKI_ROA_NOT_IN_DFZ)

        # Detect route objects in unexpected IRR
        if s.irr_expected_rir and s.irr_routes and not s.irr_routes_expected_rir:
            s.add_message(MessageType.EXPECTED_IRR_NO_ROUTE_OBJECT, irr=s.irr_expected_rir)

        # Check route objects against origins
        if s.bgp_origins - s.irr_origins:
            if s.bgp_origins.intersection(s.irr_origins):
                s.add_message(MessageType.NO_ROUTE_OBJECTS_FOR_SOME_ORIGINS)
            else:
                s.add_message(MessageType.NO_ROUTE_OBJECTS_MATCH_ORIGIN)
        elif s.irr_routes_expected_rir and s.bgp_origins - s.irr_origins_expected_rir:
            s.add_message(MessageType.EXPECTED_IRR_ORIGIN_MISMATCH, irr=s.irr_expected_rir)
        elif s.irr_origins_not_expected_rir and s.bgp_origins - s.irr_origins_not_expected_rir:
            s.add_message(MessageType.OTHER_IRR_ORIGIN_MISMATCH, irr=s.irr_expected_rir)
        elif len(s.irr_origins) > 1 and len(s.bgp_origins) == 1:
            s.add_message(MessageType.MULTIPLE_IRR_ORIGINS_SINGLE_DFZ_ORIGIN)

        # Detect RPKI situation
        if s.rpki_origins and s.bgp_origins - s.rpki_origins:
            s.add_message(MessageType.RPKI_ORIGIN_MISMATCH)
        if any([r.rpki_status == RPKIStatus.invalid for r in s.irr_routes_all]):
            s.add_message(MessageType.RPKI_INVALID_ROUTE_OBJECTS)
        elif s.irr_routes and all(
            [r.rpki_status == RPKIStatus.not_found for r in s.irr_routes_all]
        ):
            s.add_message(MessageType.NO_RPKI_ROA)

        for name, special_use_prefix in SPECIAL_USE_SPACE:
            if s.prefix.overlaps(special_use_prefix):
                s.add_message(MessageType.SPECIAL_USE_OVERLAP, name=name, prefix=special_use_prefix)

        s.finalise_status()
