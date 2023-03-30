"""add_last_data_import

Revision ID: 5b62d14388b0
Revises: 484f38cffab1
Create Date: 2023-03-29 15:41:32.350720

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5b62d14388b0"
down_revision = "484f38cffab1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "last_data_import",
        sa.Column("last_data_import", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table("last_data_import")
