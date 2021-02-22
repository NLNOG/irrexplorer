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
class PrefixSummary:
    prefix: IPNetwork = field(metadata=ip_field_metadata)
    irr_routes: Dict[str, List[PrefixIRRDetail]] = field(default_factory=lambda: defaultdict(list))
    bgp_origins: Set[int] = field(default_factory=set)
    rir: Optional[RIR] = None
    special_use_type: Optional[str] = None
