"""alter admin user table add payment

Revision ID: 1bb274a41973
Revises: 3511ac302fa7
Create Date: 2025-10-08 15:21:14.441643

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1bb274a41973'
down_revision: Union[str, Sequence[str], None] = '3511ac302fa7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("admin_user", sa.Column("total_payable", sa.Integer(), nullable=True, server_default="0"), schema="core")
    op.add_column("admin_user", sa.Column("total_due", sa.Integer(), nullable=True, server_default="0"), schema="core")
    op.add_column("admin_user", sa.Column("total_payment", sa.Integer(), nullable=True, server_default="0"), schema="core")


def downgrade() -> None:
    op.drop_column("admin_user", "total_due", schema="core")
    op.drop_column("admin_user", "total_payable", schema="core")
    op.drop_column("admin_user", "total_payment", schema="core")
