import enum
from collections import defaultdict
from dataclasses import dataclass, field
from ipaddress import IPv4Network, IPv6Network, ip_network
from typing import Dict, List, Optional, Set, Union

from dataclasses_json import LetterCase, config, dataclass_json
from marshmallow import fields

IPNetwork = Union[IPv4Network, IPv6Network]


class DataSource(enum.Enum):
    RIRSTATS = "RIRSTATS"
    BGP = "BGP"
    IRR = "IRR"
    SPECIAL_USE = "SPECIAL_USE"


class RIR(enum.Enum):
    RIPENCC = "RIPE NCC"
    ARIN = "ARIN"
    AFRINIC = "AFRINIC"
    LACNIC = "LACNIC"
    APNIC = "APNIC"


class RPKIStatus(enum.Enum):
    valid = "VALID"
    invalid = "INVALID"
    not_found = "NOT_FOUND"


RIR_EXPECTED_IRR = {
    RIR.RIPENCC: "RIPE",
}


class MessageCategory(enum.Enum):
    # Order from most severe to least severe
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"


# Prepare the serializer for dataclass_json for IPv4/6Network
ip_field_metadata = config(
    encoder=str,
    decoder=ip_network,
    mm_field=fields.Str(),
)


@dataclass
class RouteInfo:
    source: DataSource
    prefix: IPNetwork = field(metadata=ip_field_metadata)
    asn: Optional[int] = None
    rir: Optional[RIR] = None
    special_use_type: Optional[str] = None
    rpsl_pk: Optional[str] = None
    irr_source: Optional[str] = None
    rpki_status: Optional[RPKIStatus] = None
    rpki_max_length: Optional[int] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PrefixIRRDetail:
    asn: int
    rpsl_pk: Optional[str] = None
    rpki_status: Optional[RPKIStatus] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ReportMessage(object):
    category: MessageCategory
    text: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PrefixSummary:
    prefix: IPNetwork = field(metadata=ip_field_metadata)
    messages: List[ReportMessage] = field(default_factory=list)
    category_overall: Optional[MessageCategory] = None
    # Key for irr_routes is the IRR source (not including RPKI)
    irr_routes: Dict[str, List[PrefixIRRDetail]] = field(default_factory=lambda: defaultdict(list))
    rpki_routes: List[PrefixIRRDetail] = field(default_factory=list)
    bgp_origins: Set[int] = field(default_factory=set)
    rir: Optional[RIR] = None
    special_use_type: Optional[str] = None

    def finalise_status(self):
        if not self.messages:
            self.success("Everything looks good")
        ordered_categories = [m for m in MessageCategory]
        self.messages.sort(key=lambda m: ordered_categories.index(m.category))
        for category in MessageCategory:
            if [m for m in self.messages if m.category == category]:
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
        return {rpki.asn for rpki in self.rpki_routes if rpki.asn != 0}

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
        if not self.irr_expected_rir:
            return []
        try:
            return self.irr_routes[self.irr_expected_rir]
        except KeyError:
            return []

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
