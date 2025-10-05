"""update admin user table

Revision ID: 7ea563dd24f1
Revises: d04a22b53dd2
Create Date: 2025-10-05 10:40:03.088666

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7ea563dd24f1'
down_revision: Union[str, Sequence[str], None] = 'd04a22b53dd2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("admin_user", sa.Column("passport_no", sa.String(), nullable=True), schema="core")
    op.add_column("admin_user", sa.Column("passport_expiry_date", sa.String(), nullable=True), schema="core")
    op.add_column("admin_user", sa.Column("passport_address", sa.String(), nullable=True), schema="core")
    op.add_column("admin_user", sa.Column("passport_dob", sa.String(), nullable=True), schema="core")
    op.drop_column("admin_user", "username", schema="core")
    op.drop_column("admin_user", "password", schema="core")


def downgrade() -> None:
    # ✅ Drop the same columns we added
    op.drop_column("admin_user", "passport_dob", schema="core")
    op.drop_column("admin_user", "passport_address", schema="core")
    op.drop_column("admin_user", "passport_expiry_date", schema="core")
    op.drop_column("admin_user", "passport_no", schema="core")