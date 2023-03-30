"""add_rir_registrobr

Revision ID: 1a8103c368a2
Revises: 484f38cffab1
Create Date: 2023-03-30 15:51:13.935002

"""
from alembic import op
from sqlalchemy.exc import ProgrammingError

# revision identifiers, used by Alembic.
revision = "1a8103c368a2"
down_revision = "484f38cffab1"
branch_labels = None
depends_on = None


def upgrade():
    # downgrade() can't remove this entry from the enum, so if this migration
    # is reverted and then re-applied, altering the enum will fail
    with op.get_context().autocommit_block():
        try:
            op.execute("ALTER TYPE rir ADD VALUE 'REGISTROBR'")
        except ProgrammingError as pe:
            if "DuplicateObject" not in str(pe):
                raise pe


def downgrade():
    pass
