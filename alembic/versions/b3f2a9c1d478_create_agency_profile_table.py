"""create agency profile table

Revision ID: b3f2a9c1d478
Revises: 6aa3dfe8fea0
Create Date: 2026-09-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3f2a9c1d478'
down_revision: Union[str, Sequence[str], None] = '6aa3dfe8fea0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agency_profile",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("sl_no", sa.Integer(), nullable=True),
        sa.Column("hl", sa.String(), nullable=False),
        sa.Column("agency_name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("pre_reg", sa.Integer(), nullable=True),
        sa.Column("reg", sa.Integer(), nullable=True),
        sa.Column("total", sa.Integer(), nullable=True),
        sa.Column("source_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(),
            server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"),
            nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(),
            server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"),
            nullable=False,
        ),
        sa.Column("created_by", sa.String(), nullable=True),
        sa.Column("updated_by", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        schema="core",
    )
    op.create_index(
        op.f("ix_core_agency_profile_id"), "agency_profile", ["id"], unique=False, schema="core"
    )
    op.create_index(
        op.f("ix_core_agency_profile_hl"), "agency_profile", ["hl"], unique=True, schema="core"
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_core_agency_profile_hl"), table_name="agency_profile", schema="core")
    op.drop_index(op.f("ix_core_agency_profile_id"), table_name="agency_profile", schema="core")
    op.drop_table("agency_profile", schema="core")
