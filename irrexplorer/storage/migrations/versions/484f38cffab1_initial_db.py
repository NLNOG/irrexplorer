"""initial_db

Revision ID: 484f38cffab1
Revises:
Create Date: 2021-02-21 15:14:38.561121

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '484f38cffab1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'bgp',
        sa.Column("ip_version", sa.Integer(), index=True, nullable=False),
        sa.Column('asn', sa.Integer(), nullable=False),
        sa.Column('prefix', postgresql.CIDR(), nullable=False)
    )
    op.create_index(op.f('ix_bgp_asn'), 'bgp', ['asn'], unique=False)
    op.create_index('ix_bgp_prefix', 'bgp', [sa.text('prefix inet_ops')],
                    unique=False,
                    postgresql_using='spgist')

    op.create_table(
        'rirstats',
        sa.Column("ip_version", sa.Integer(), index=True, nullable=False),
        sa.Column('rir', sa.Enum('RIPENCC', 'ARIN', 'AFRINIC', 'LACNIC', 'APNIC', name='rir'),
                  nullable=False),
        sa.Column('prefix', postgresql.CIDR(), nullable=False)
    )
    op.create_index('ix_rirstats_prefix', 'rirstats', [sa.text('prefix inet_ops')],
                    unique=False,
                    postgresql_using='spgist')


def downgrade():
    op.drop_index(op.f('ix_rirstats_prefix'), table_name='rirstats')
    op.drop_table('rirstats')
    op.drop_index(op.f('ix_bgp_asn'), table_name='bgp')
    op.drop_index(op.f('ix_bgp_prefix'), table_name='bgp')
    op.drop_table('bgp')
