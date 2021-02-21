import enum


class RIR(enum.Enum):
    RIPENCC = 'RIPE NCC'
    ARIN = 'ARIN'
    AFRINIC = 'AFRINIC'
    LACNIC = 'LACNIC'
    APNIC = 'APNIC'


RIR_EXPECTED_IRR = {
    RIR.RIPENCC: 'RIPE',
}
