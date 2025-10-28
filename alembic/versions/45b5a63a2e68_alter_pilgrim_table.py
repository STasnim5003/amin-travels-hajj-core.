"""alter pilgrim table

Revision ID: 45b5a63a2e68
Revises: b786e4fb02e4
Create Date: 2025-10-28 14:37:20.576872

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45b5a63a2e68'
down_revision: Union[str, Sequence[str], None] = 'b786e4fb02e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("pilgrim_data", sa.Column("pre_reg_voucher", sa.String(), nullable=True),schema='core')
    op.add_column("pilgrim_data", sa.Column("reg_voucher", sa.String(), nullable=True),schema='core')
    op.add_column("pilgrim_data", sa.Column("passport_dob", sa.String(), nullable=True),schema='core')
    op.add_column("pilgrim_data", sa.Column("passport_type", sa.String(), nullable=True),schema='core')


def downgrade() -> None:
    op.drop_column("pilgrim_data", "pre_reg_voucher", schema='core')
    op.drop_column("pilgrim_data", "reg_voucher", schema='core')
    op.drop_column("pilgrim_data", "passport_dob", schema='core')
    op.drop_column("pilgrim_data", "passport_type", schema='core')
