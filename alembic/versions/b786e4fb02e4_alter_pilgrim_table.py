"""alter pilgrim table

Revision ID: b786e4fb02e4
Revises: a69a9f9949d2
Create Date: 2025-10-27 20:24:12.142608

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b786e4fb02e4'
down_revision: Union[str, Sequence[str], None] = 'a69a9f9949d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("pilgrim_data", sa.Column("voucher", sa.String(), nullable=True),
                  schema='core')


def downgrade() -> None:
    """Downgrade schema."""
    pass
