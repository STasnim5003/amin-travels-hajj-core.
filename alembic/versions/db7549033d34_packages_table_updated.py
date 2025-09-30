"""packages table updated

Revision ID: db7549033d34
Revises: fa719f172387
Create Date: 2025-09-29 23:38:50.623242

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'db7549033d34'
down_revision: Union[str, Sequence[str], None] = 'fa719f172387'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("packages", sa.Column("duration_range", postgresql.JSONB(astext_type=sa.TEXT())), schema="core")
    op.add_column("packages", sa.Column("flight_date", postgresql.JSONB(astext_type=sa.TEXT())), schema="core")
    op.add_column("packages", sa.Column("bed_type", postgresql.JSONB(astext_type=sa.TEXT())), schema="core")
    op.add_column("packages", sa.Column("return_ticket", sa.String(), nullable=True), schema="core")
    op.add_column("packages", sa.Column("fixed_or_shifting", sa.String(), nullable=True), schema="core")
    op.add_column("packages", sa.Column("food_menu_id", sa.Integer(), nullable=True), schema="core")
    op.add_column("packages", sa.Column("ziara_id", postgresql.JSONB(astext_type=sa.TEXT())), schema="core")
    op.add_column("packages", sa.Column("special_services", postgresql.JSONB(astext_type=sa.TEXT())), schema="core")
    op.add_column("packages", sa.Column("other_services", postgresql.JSONB(astext_type=sa.TEXT())), schema="core")
    op.add_column("packages", sa.Column("route_id", sa.Integer(), nullable=True), schema="core")
    op.add_column("packages", sa.Column("airlines", sa.String(), nullable=True), schema="core")


    op.create_table(
        "food_menu",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("agency_name", sa.String(), nullable=True),
        sa.Column("items", postgresql.JSONB(astext_type=sa.TEXT()), nullable=True),
        sa.Column('is_publish', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=True,
                  onupdate=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'")),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        schema="core"
    )

    # Create route table
    op.create_table(
        "route",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column('is_publish', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column("agency_name", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=True, onupdate=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'")),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        schema="core"
    )

    # Create ziara table
    op.create_table(
        "ziara",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("pic", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=False),
        sa.Column("google_map_location", sa.String(), nullable=False),
        sa.Column("agency_name", sa.String(), nullable=True),
        sa.Column("area", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=True,
                  onupdate=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'")),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        schema="core"
    )
    # add ons table
    op.create_table(
        "add_ons_service",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("category", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("price", sa.String(), nullable=False),
        sa.Column("agency_name", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=True,
                  onupdate=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'")),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        schema="core"
    )

    op.alter_column("admin","passport_copy",schema="core",existing_type=sa.dialects.postgresql.JSONB(astext_type=sa.Text()),nullable=True)
    op.alter_column("admin","logo",schema="core",existing_type=sa.dialects.postgresql.JSONB(astext_type=sa.Text()),nullable=True)


def downgrade() -> None:
    op.drop_column("packages", "duration_range", schema="core")
    op.drop_column("packages", "flight_date", schema="core")
    op.drop_column("packages", "bed_type", schema="core")
    op.drop_column("packages", "return_ticket", schema="core")
    op.drop_column("packages", "fixed_or_shifting", schema="core")
    op.drop_column("packages", "food_menu_id", schema="core")
    op.drop_column("packages", "ziara_id", schema="core")
    op.drop_column("packages", "special_services", schema="core")
    op.drop_column("packages", "other_services", schema="core")
    op.drop_column("packages", "route_id", schema="core")
    op.drop_column("packages", "airlines", schema="core")

    op.drop_table("ziara", schema="core")
    op.drop_table("food_menu", schema="core")
    op.drop_table("route", schema="core")
    op.drop_table("add_ons_service", schema="core")