import enum


class RIR(enum.Enum):
    RIPENCC = 'RIPE NCC'
    ARIN = 'ARIN'
    AFRNIC = 'AfriNIC'
    LACNIC = 'LACNIC'
    APNIC = 'APNIC'


RIR_EXPECTED_IRR = {
    RIR.RIPENCC: 'RIPE',
}
