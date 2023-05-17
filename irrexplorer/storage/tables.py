import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

from irrexplorer.state import RIR

sa_metadata = sa.MetaData()

bgp = sa.Table(
    "bgp",
    sa_metadata,
    sa.Column("asn", sa.BigInteger, index=True, nullable=False),
    sa.Column("prefix", pg.CIDR, nullable=False),
    sa.Index("ix_bgp_prefix", sa.text("prefix inet_ops"), postgresql_using="gist"),
)

rirstats = sa.Table(
    "rirstats",
    sa_metadata,
    sa.Column("rir", sa.Enum(RIR), nullable=False),
    sa.Column("prefix", pg.CIDR, nullable=False),
    sa.Index("ix_rirstats_prefix", sa.text("prefix inet_ops"), postgresql_using="gist"),
)

last_data_import = sa.Table(
    "last_data_import",
    sa_metadata,
    sa.Column("last_data_import", sa.DateTime(timezone=True), nullable=False),
)
