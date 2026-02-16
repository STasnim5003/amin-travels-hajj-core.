"""create vendor prices table

Revision ID: 26bc1a639e35
Revises: 95a822c04fca
Create Date: 2026-02-16 14:21:56.574969

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '26bc1a639e35'
down_revision: Union[str, Sequence[str], None] = '95a822c04fca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "umrah_vendor_prices",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("umrah_requisition_id", sa.BigInteger(), nullable=False),
        sa.Column("hotel_vendors_price", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("transport_vendors_price", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("air_ticket_vendors_price", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("visa_vendors_price", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("train_vendors_price", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ziara_vendors_price", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("food_vendors_price", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("others_vendors_price", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column("created_by", sa.String(), nullable=True),
        sa.Column("updated_by", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("true")),
        schema="core",
    )


def downgrade() -> None:
    op.drop_table("umrah_vendor_prices", schema="core")
