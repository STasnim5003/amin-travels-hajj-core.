"""alter package table

Revision ID: 529048b75c0b
Revises: f2f840af7ecf
Create Date: 2025-10-06 23:02:17.973840

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '529048b75c0b'
down_revision: Union[str, Sequence[str], None] = 'f2f840af7ecf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("packages", sa.Column("agency_name", sa.String(), nullable=True),schema="core")
    op.drop_column("packages", "ziara_id", schema="core")
    op.add_column("packages", sa.Column("ziara_id", sa.Integer(), nullable=True),schema="core")



def downgrade() -> None:
    """Downgrade schema."""
    pass
