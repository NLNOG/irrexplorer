from irrexplorer.state import RIR

BGP_SOURCE = 'http://lg01.infra.ring.nlnog.net/table.txt'
DATABASE_URL = 'postgresql://localhost/irrexplorer'

RIRSTATS_URL = {
    RIR.RIPENCC: 'https://ftp.ripe.net/ripe/stats/delegated-ripencc-latest',
    RIR.ARIN: 'https://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest',
    RIR.AFRINIC: 'https://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-latest',
    RIR.LACNIC: 'https://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-latest',
    RIR.APNIC: 'https://ftp.apnic.net/stats/apnic/delegated-apnic-latest',
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
