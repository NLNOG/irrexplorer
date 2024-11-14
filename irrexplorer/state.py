import enum
from dataclasses import dataclass
from ipaddress import IPv4Network, IPv6Network
from typing import Optional, Union

IPNetwork = Union[IPv4Network, IPv6Network]


class DataSource(enum.Enum):
    RIRSTATS = "RIRSTATS"
    BGP = "BGP"
    IRR = "IRR"


class RIR(enum.Enum):
    RIPENCC = "RIPE NCC"
    ARIN = "ARIN"
    AFRINIC = "AFRINIC"
    LACNIC = "LACNIC"
    APNIC = "APNIC"
    REGISTROBR = "Registro.BR"


class NIR(enum.Enum):
    """
    This enum classifies specific RIR entries that are considered NIRs.
    Each entry in the enum represents a recognized NIR with its official designation.
    """
    REGISTROBR = "Registro.BR"  # Represents the Brazilian Internet Registry


class RPKIStatus(enum.Enum):
    valid = "VALID"
    invalid = "INVALID"
    not_found = "NOT_FOUND"


RIR_EXPECTED_IRR = {
    RIR.AFRINIC: "AFRINIC",
    RIR.APNIC: "APNIC",
    RIR.ARIN: "ARIN",
    RIR.LACNIC: "LACNIC",
    RIR.RIPENCC: "RIPE",
    RIR.REGISTROBR: "TC",
}


@dataclass
class RouteInfo:
    source: DataSource
    prefix: IPNetwork
    asn: Optional[int] = None
    rir: Optional[RIR] = None
    rpsl_pk: Optional[str] = None
    irr_source: Optional[str] = None
    rpsl_text: Optional[str] = None
    rpki_status: Optional[RPKIStatus] = None
    rpki_max_length: Optional[int] = None
