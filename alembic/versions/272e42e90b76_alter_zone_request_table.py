"""alter zone request table

Revision ID: 272e42e90b76
Revises: c826b418a40e
Create Date: 2026-03-03 00:00:43.902990

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '272e42e90b76'
down_revision: Union[str, Sequence[str], None] = 'c826b418a40e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('zone_request', sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.drop_column('zone_request', 'zone_wise_tent_in_mina', schema='core')
    op.drop_column('zone_request', 'zone_wise_pilgrims', schema='core')
    op.drop_column('zone_request', 'service_company_in_mina_arafat', schema='core')
    op.drop_column('zone_request', 'package_in_mina_arafat', schema='core')

def downgrade() -> None:
    op.add_column('zone_request', sa.Column('package_in_mina_arafat', sa.Text(), nullable=True), schema='core')
    op.add_column('zone_request', sa.Column('service_company_in_mina_arafat', sa.Text(), nullable=True), schema='core')
    op.add_column('zone_request', sa.Column('zone_wise_pilgrims', sa.Text(), nullable=True), schema='core')
    op.add_column('zone_request', sa.Column('zone_wise_tent_in_mina', sa.Text(), nullable=True), schema='core')
    op.drop_column('zone_request', 'details', schema='core')
