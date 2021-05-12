import databases
from starlette.config import Config

from irrexplorer.state import RIR

config = Config(".env")

DEBUG = config("DEBUG", cast=bool, default=False)
TESTING = config("TESTING", cast=bool, default=False)

HTTP_PORT = config("HTTP_PORT", cast=int, default=8000)
HTTP_WORKERS = config("HTTP_WORKERS", cast=int, default=4)

BGP_SOURCE = config("BGP_SOURCE", default="http://lg01.infra.ring.nlnog.net/table.txt")
DATABASE_URL = config("DATABASE_URL", cast=databases.DatabaseURL)

if TESTING:
    DATABASE_URL = DATABASE_URL.replace(database="test_" + DATABASE_URL.database)
else:  # pragma: no cover
    # IRRD_ENDPOINT is read at connection time to allow tests to change it,
    # load it here if not testing to trigger an error earlier if it's missing.
    config("IRRD_ENDPOINT")

RIRSTATS_URL = {
    RIR.RIPENCC: config(
        key="RIRSTATS_URL_RIPENCC",
        default="https://ftp.ripe.net/ripe/stats/delegated-ripencc-latest",
    ),
    RIR.ARIN: config(
        key="RIRSTATS_URL_ARIN",
        default="https://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest",
    ),
    RIR.AFRINIC: config(
        key="RIRSTATS_URL_AFRINIC",
        default="https://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-latest",
    ),
    RIR.LACNIC: config(
        key="RIRSTATS_URL_LACNIC",
        default="https://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-latest",
    ),
    RIR.APNIC: config(
        key="RIRSTATS_URL_APNIC", default="https://ftp.apnic.net/stats/apnic/delegated-apnic-latest"
    ),
}

BGP_IPV4_LENGTH_CUTOFF = config("BGP_IPV4_LENGTH_CUTOFF", cast=int, default=29)
BGP_IPV6_LENGTH_CUTOFF = config("BGP_IPV6_LENGTH_CUTOFF", cast=int, default=124)

MINIMUM_PREFIX_SIZE = {
    4: config("MINIMUM_PREFIX_SIZE_IPV4", cast=int, default=9),
    6: config("MINIMUM_PREFIX_SIZE_IPV4", cast=int, default=29),
}

SPECIAL_USE_SPACE = [
    ("RFC1122", "0.0.0.0/8", 4),
    ("RFC1918", "10.0.0.0/8", 4),
    ("RFC6598", "100.64.0.0/10", 4),
    ("LOOPBACK", "127.0.0.0/8", 4),
    ("RFC1918", "172.16.0.0/12", 4),
    ("RFC5736", "192.0.0.0/24", 4),
    ("RFC1918", "192.168.0.0/16", 4),
    ("RFC3927", "169.254.0.0/16", 4),
    ("RFC5737", "192.0.2.0/24", 4),
    ("RFC2544", "198.18.0.0/15", 4),
    ("RFC5737", "198.51.100.0/24", 4),
    ("RFC5737", "203.0.113.0/24", 4),
    ("CLASS-E", "240.0.0.0/4", 4),
    ("IPv4-mapped", "::ffff:0:0/96", 6),
    ("IPv4-compatible", "::/96", 6),
    ("IPv6-ULA", "fc00::/7", 6),
]
