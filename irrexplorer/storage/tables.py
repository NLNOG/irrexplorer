import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

from irrexplorer.state import RIR

metadata = sa.MetaData()

bgp = sa.Table(
    "bgp",
    metadata,
    sa.Column("ip_version", sa.Integer, index=True, nullable=False),
    sa.Column("asn", sa.BigInteger, index=True, nullable=False),
    sa.Column("prefix", pg.CIDR, nullable=False),
    sa.Index("ix_bgp_prefix", sa.text("prefix inet_ops"), postgresql_using="gist"),
)

rirstats = sa.Table(
    "rirstats",
    metadata,
    sa.Column("ip_version", sa.Integer, index=True, nullable=False),
    sa.Column("rir", sa.Enum(RIR), nullable=False),
    sa.Column("prefix", pg.CIDR, nullable=False),
    sa.Index("ix_rirstats_prefix", sa.text("prefix inet_ops"), postgresql_using="gist"),
)
