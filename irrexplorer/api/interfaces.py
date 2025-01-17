import enum
from collections import defaultdict
from dataclasses import dataclass, field
from ipaddress import ip_network
from typing import Dict, List, Optional, Set

import marshmallow
from dataclasses_json import LetterCase, config, dataclass_json

from irrexplorer.state import RIR, RIR_EXPECTED_IRR, IPNetwork, RPKIStatus

"""
This file defines a number of properties that essentially form the
interface of the API. These objects are created by the collector
in storage, enriched by the report module in api, converted
to JSON, and returned to the client.

Several method refer to the concept of an "expected IRR". This
means that if rirstats says a prefix is RIPE NCC space, the
route object is expected in RIPE. An object in RADB would be
from the not expected IRR. Not all prefixes have an expected IRR.
"""


class MessageCategory(enum.Enum):
    # Must be ordered from most severe to least severe, order is translated
    # into goodness_overall, used for sorting in frontend
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"


class ObjectClass(enum.Enum):
    # Not complete, used in limited scopes
    ROUTESET = "route-set"
    ASSET = "as-set"


# dataclass_json needs a serializer IPv4/6Network
ip_field_metadata = config(
    encoder=str,
    decoder=ip_network,
    mm_field=marshmallow.fields.Str(),
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PrefixIRRDetail:
    asn: int
    rpsl_text: str
    rpsl_pk: Optional[str] = None
    rpki_status: Optional[RPKIStatus] = None
    rpki_max_length: Optional[int] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ReportMessage(object):
    category: MessageCategory
    text: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PrefixSummary:
    # This first set of fields has to be filled with data,
    # if applicable.
    prefix: IPNetwork = field(metadata=ip_field_metadata)
    rir: Optional[RIR] = None
    rpki_routes: List[PrefixIRRDetail] = field(default_factory=list)
    bgp_origins: Set[int] = field(default_factory=set)
    # Key for irr_routes is the IRR source (not including RPKI)
    irr_routes: Dict[str, List[PrefixIRRDetail]] = field(default_factory=lambda: defaultdict(list))

    # Message from the report module, set through the
    # convenience method info(), warning(), etc.
    messages: List[ReportMessage] = field(default_factory=list)

    # Autogenerated by finalise_status()
    # The worst category of message on this summary, indicating overall status
    category_overall: Optional[MessageCategory] = None
    # category_overall converted into a number for sorting
    goodness_overall: Optional[int] = 0
    # Numerical IP plus prefix length. Used as sorting key in the frontend.
    prefix_sort_key_ip_prefix: Optional[str] = None
    # (128 - prefix length) plus numerical IP. Used as sorting key in the frontend.
    prefix_sort_key_reverse_networklen_ip: Optional[str] = None

    def finalise_status(self):
        """
        Set a few properties that depend on others.
        Should be called before returning to the user.
        """
        self.prefix_sort_key_ip_prefix = f"{self.prefix.network_address._ip}/{self.prefix.prefixlen}"
        self.prefix_sort_key_reverse_networklen_ip = f"{128 - self.prefix.prefixlen}-{self.prefix.network_address._ip}"
        if not self.messages:
            self.success("Everything looks good")

        ordered_categories = [m for m in MessageCategory]
        self.messages.sort(key=lambda m: ordered_categories.index(m.category))

        for idx, category in enumerate(MessageCategory):
            if [m for m in self.messages if m.category == category]:
                self.goodness_overall = idx
                self.category_overall = category
                return

    @property
    def irr_routes_all(self) -> List[PrefixIRRDetail]:
        return [irr for irrs in self.irr_routes.values() for irr in irrs]

    @property
    def irr_origins(self) -> Set[int]:
        return {irr.asn for irr in self.irr_routes_all}

    @property
    def rpki_origins(self) -> Set[int]:
        return {rpki.asn for rpki in self.rpki_routes}

    @property
    def irr_origins_not_expected_rir(self) -> Set[int]:
        return {
            irr.asn
            for name, irrs in self.irr_routes.items()
            for irr in irrs
            if name != self.irr_expected_rir
        }

    @property
    def irr_origins_expected_rir(self) -> Set[int]:
        return {irr.asn for irr in self.irr_routes_expected_rir}

    @property
    def irr_expected_rir(self) -> Optional[str]:
        return RIR_EXPECTED_IRR.get(self.rir) if self.rir else None

    @property
    def irr_routes_expected_rir(self) -> List[PrefixIRRDetail]:
        if not self.irr_expected_rir or self.irr_expected_rir not in self.irr_routes:
            return []
        return self.irr_routes[self.irr_expected_rir]

    def add_message(self, category: MessageCategory, text: str):
        self.messages.append(ReportMessage(category=category, text=text))

    def success(self, text: str):
        self.add_message(MessageCategory.SUCCESS, text)

    def info(self, text: str):
        self.add_message(MessageCategory.INFO, text)

    def warning(self, text: str):
        self.add_message(MessageCategory.WARNING, text)

    def danger(self, text: str):
        self.add_message(MessageCategory.DANGER, text)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ASNPrefixes:
    direct_origin: List[PrefixSummary] = field(default_factory=list)
    overlaps: List[PrefixSummary] = field(default_factory=list)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MemberOf:
    irrs_seen: List[str] = field(default_factory=list)
    sets_per_irr: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class SetExpansion:
    name: str
    source: str
    depth: int
    path: List[str]
    members: List[str]
