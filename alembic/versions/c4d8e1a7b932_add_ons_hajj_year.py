"""add_ons_hajj_year

Revision ID: c4d8e1a7b932
Revises: b7e3c91d4a20
Create Date: 2026-10-04 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4d8e1a7b932'
down_revision: Union[str, Sequence[str], None] = 'b7e3c91d4a20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('add_ons_service', sa.Column('hajj_year', sa.Integer(), nullable=True), schema='core')
    # Today's catalog already holds the 2027 prices (edited after Hajj 2026 closed).
    op.execute("UPDATE core.add_ons_service SET hajj_year = 2027")
    op.alter_column('add_ons_service', 'hajj_year', nullable=False, schema='core')
    # Rebuild 2026 at the price most 2026 pilgrims were billed for each add-on (fallback: current price).
    op.execute("""
        INSERT INTO core.add_ons_service (name, category, price, agency_name, hajj_year,
                                          created_at, updated_at, created_by, updated_by, is_active)
        SELECT a.name, a.category,
               COALESCE((
                   SELECT e.value
                   FROM core.pilgrim_data p,
                        jsonb_each_text(p.add_ons_services::jsonb) e
                   WHERE p.hajj_year = 2026
                     AND p.group_name = a.agency_name
                     AND jsonb_typeof(p.add_ons_services::jsonb) = 'object'
                     AND lower(btrim(e.key)) = lower(btrim(a.name))
                   GROUP BY e.value
                   ORDER BY count(*) DESC
                   LIMIT 1
               ), a.price),
               a.agency_name, 2026, a.created_at, a.created_at, a.created_by, a.created_by, a.is_active
        FROM core.add_ons_service a
        WHERE a.hajj_year = 2027
    """)
    op.execute("""
        CREATE UNIQUE INDEX uq_add_ons_agency_year_name
        ON core.add_ons_service (agency_name, hajj_year, lower(btrim(name)))
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS core.uq_add_ons_agency_year_name")
    op.drop_column('add_ons_service', 'hajj_year', schema='core')
