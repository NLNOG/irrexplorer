"""
Every message that prefix reports can include, with its explanation.
The frontend gets these through /api/messages/.
"""

import enum
import re


class MessageCategory(enum.Enum):
    # Must be ordered from most severe to least severe, order is translated
    # into goodness_overall, used for sorting in frontend
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"


class MessageType(enum.Enum):
    # The key is part of the API, and derived from the member name.
    # The text may have placeholders, filled in by PrefixSummary.add_message().
    # Keep members ordered from most to least severe, as the explanation of
    # messages lists them in this order.

    def __init__(self, category: MessageCategory, text: str, explanation: str):
        self.category = category
        self.text = text
        self.explanation = explanation

    @property
    def key(self) -> str:
        return self.name.lower()

    NO_ROUTE_OBJECTS_MATCH_ORIGIN = (
        MessageCategory.DANGER,
        "No route objects match DFZ origin",
        "This prefix is seen in the DFZ, but no route object matches any of its origins. This can "
        "have a significant impact on reachability, as networks that filter on IRR data may reject "
        "its announcements. You should create route objects for its origins if they are legitimate.",
    )
    NO_ROUTE_OBJECTS_FOR_SOME_ORIGINS = (
        MessageCategory.DANGER,
        "No route objects for some DFZ origins",
        "This prefix is seen in the DFZ with multiple origins, but only some of them have route "
        "objects. Networks that filter on IRR data may reject the announcements from the others. "
        "You should create route objects for those origins if they are legitimate. Otherwise, "
        "their announcements are a hijack or a misconfiguration.",
    )
    EXPECTED_IRR_ORIGIN_MISMATCH = (
        MessageCategory.DANGER,
        "Expected route object in {irr}, but BGP origin does not match. "
        "Objects from other IRRs do match BGP origin",
        "The IRR of the RIR responsible for this prefix has route objects for it, but some origins "
        "seen in the DFZ only have route objects in other IRRs. If those origins are legitimate, "
        "you should add route objects for them to the RIR's IRR, which is authoritative for this "
        "prefix.",
    )
    RPKI_ORIGIN_MISMATCH = (
        MessageCategory.DANGER,
        "RPKI origin does not match BGP origin",
        "This prefix has a ROA, but some origins seen in the DFZ have no ROA for it. Unless a ROA "
        "for a less specific prefix allows those origins, their announcements are RPKI-invalid. "
        "Networks increasingly drop RPKI-invalid routes, so this can affect reachability. You "
        "should create ROAs for those origins if they are legitimate.",
    )
    RPKI_INVALID_ROUTE_OBJECTS = (
        MessageCategory.DANGER,
        "RPKI-invalid route objects found",
        "At least one route object for this prefix is RPKI-invalid. A ROA covers this prefix, "
        "but no ROA allows that object's origin at this prefix length. You should check whether "
        "the ROAs or the route objects are wrong or outdated, and fix them.",
    )
    SPECIAL_USE_OVERLAP = (
        MessageCategory.DANGER,
        "Overlaps with {name} special use prefix {prefix}",
        "This prefix overlaps with special use address space, which should not be announced in the "
        "DFZ or have route objects.",
    )
    EXPECTED_IRR_NO_ROUTE_OBJECT = (
        MessageCategory.WARNING,
        "Expected route object in {irr}, but only found in other IRRs",
        "The IRR of the RIR responsible for this prefix has no route objects for it, but other IRRs "
        "do. If this prefix is in use, you should add a route object to the RIR's IRR, which is "
        "authoritative for this prefix.",
    )
    OTHER_IRR_ORIGIN_MISMATCH = (
        MessageCategory.WARNING,
        "Expected route object in {irr} matches BGP origin, "
        "but non-matching objects exist in other IRRs",
        "The route objects in the IRR of the RIR responsible for this prefix match every origin "
        "seen in the DFZ, but those in other IRRs do not. If the route objects in other IRRs are "
        "outdated, you should have them removed, as they let their origin pass IRR-based filters.",
    )
    MULTIPLE_IRR_ORIGINS_SINGLE_DFZ_ORIGIN = (
        MessageCategory.WARNING,
        "Multiple route objects exist with different origins, but DFZ only has one",
        "There are route objects for this prefix with different origins, but only one of those "
        "origins is seen in the DFZ. If the route objects for the other origins are outdated, you "
        "should remove them.",
    )
    ROUTE_OBJECTS_NOT_IN_DFZ = (
        MessageCategory.INFO,
        "Route objects exist, but prefix not seen in DFZ",
        "There are route objects for this prefix, but the prefix is not seen in the DFZ. "
        "If the prefix is no longer in use, you should clean up these route objects. "
        "If you plan to announce this prefix in the future, this is harmless.",
    )
    RPKI_ROA_NOT_IN_DFZ = (
        MessageCategory.INFO,
        "RPKI ROA exists, but prefix not seen in DFZ",
        "There is a ROA for this prefix with an origin other than AS0, but the prefix is not seen "
        "in the DFZ. If the ROA allows more specific prefixes that are announced instead, you "
        "should replace it with ROAs for those prefixes, as RFC 9319 recommends. If this prefix "
        "and its more specific prefixes are no longer in use, you should replace its ROAs with a "
        "ROA for AS0.",
    )
    NO_RPKI_ROA = (
        MessageCategory.INFO,
        "No (covering) RPKI ROA found for route objects",
        "No ROA covers this prefix, so the RPKI status of its route objects is unknown. "
        "Any ROA for this prefix or a less specific prefix would cover it, whatever the ROA's "
        "maximum length. If this prefix is in use, you should create a ROA for it.",
    )
    EVERYTHING_GOOD = (
        MessageCategory.SUCCESS,
        "Everything looks good",
        "IRR explorer found no problems in the BGP, IRR and RPKI data for this prefix.",
    )


def message_catalogue() -> list:
    return [
        {
            "key": message_type.key,
            "category": message_type.category.value,
            # e.g. {irr} becomes <IRR>
            "text": re.sub(r"{(\w+)}", lambda match: f"<{match[1].upper()}>", message_type.text),
            "explanation": message_type.explanation,
        }
        for message_type in MessageType
    ]
