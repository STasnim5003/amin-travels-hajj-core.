"""alter route request restructured column

Revision ID: 0eb45edb54ee
Revises: 03d8b3bb0c48
Create Date: 2026-01-17 18:12:35.449035

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0eb45edb54ee'
down_revision: Union[str, Sequence[str], None] = '03d8b3bb0c48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('route_request', sa.Column('arrival', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('route_request', sa.Column('departure', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('route_request', sa.Column('between_cities_up', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('route_request', sa.Column('between_cities_down', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('route_request', sa.Column('mashaer', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.drop_column('route_request', 'route_type', schema='core')
    op.drop_column('route_request', 'route_name', schema='core')
    op.drop_column('route_request', 'route_price', schema='core')
    op.drop_column('route_request', 'number_of_pax', schema='core')
    op.drop_column('route_request', 'route_mapping_id', schema='core')

def downgrade() -> None:
    op.drop_column('route_request', 'arrival', schema='core')
    op.drop_column('route_request', 'departure', schema='core')
    op.drop_column('route_request', 'between_cities_up', schema='core')
    op.drop_column('route_request', 'between_cities_down', schema='core')
    op.drop_column('route_request', 'mashaer', schema='core')

