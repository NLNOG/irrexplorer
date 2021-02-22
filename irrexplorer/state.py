import enum
from dataclasses import dataclass, field
from ipaddress import IPv4Network, IPv6Network, ip_network
from typing import List, Optional, Union
from dataclasses_json import dataclass_json, LetterCase, config
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
class PrefixSourceDetail:
    source: DataSource
    asn: int
    irr_source: Optional[str] = None
    rpsl_pk: Optional[str] = None
    rpki_status: Optional[RPKIStatus] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PrefixSummary:
    prefix: IPNetwork = field(metadata=ip_field_metadata)
    details: List[PrefixSourceDetail]
    rir: Optional[RIR] = None
    special_use_type: Optional[str] = None


