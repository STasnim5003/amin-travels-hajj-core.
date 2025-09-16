"""alter admin table

Revision ID: 6e39ce8fe3c7
Revises: 15abaace8497
Create Date: 2025-09-15 16:03:31.899174

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6e39ce8fe3c7'
down_revision: Union[str, Sequence[str], None] = '15abaace8497'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("admin", sa.Column("agency_name", sa.String(), nullable=False), schema="core")
    op.add_column("admin", sa.Column("license_number", sa.String(), nullable=False), schema="core")
    op.add_column("admin", sa.Column("location", sa.String(), nullable=True), schema="core")
    op.add_column("admin", sa.Column("mobile_no", sa.String(), nullable=False), schema="core")
    op.add_column("admin", sa.Column("email", sa.String(), nullable=True), schema="core")
    op.add_column("admin", sa.Column("passport_copy", postgresql.JSONB(astext_type=sa.TEXT())), schema="core")
    op.add_column("admin", sa.Column("logo", postgresql.JSONB(astext_type=sa.TEXT())), schema="core")


def downgrade() -> None:
    op.drop_column("admin", "logo", schema="core")
    op.drop_column("admin", "email", schema="core")
    op.drop_column("admin", "mobile_no", schema="core")
    op.drop_column("admin", "location", schema="core")
    op.drop_column("admin", "license_number", schema="core")
    op.drop_column("admin", "agency_name", schema="core")
    op.drop_column("admin", "passport_copy", schema="core")