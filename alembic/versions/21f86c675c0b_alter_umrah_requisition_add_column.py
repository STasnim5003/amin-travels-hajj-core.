"""alter umrah requisition add column

Revision ID: 21f86c675c0b
Revises: df4405761de3
Create Date: 2026-04-07 15:51:52.043794

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '21f86c675c0b'
down_revision: Union[str, Sequence[str], None] = 'df4405761de3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('umrah_requisition', sa.Column('is_child_included_with_bed_transport',sa.Boolean(),nullable=False,server_default=sa.text('TRUE')),schema='core')
    op.add_column('umrah_requisition',sa.Column('confirmed_remarks', sa.String(), nullable=True), schema='core')
    op.add_column('umrah_requisition',sa.Column('reference', sa.String(), nullable=True), schema='core')
    op.add_column('umrah_requisition',sa.Column('confirmed_pilgrims_family_group', sa.String(), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('confirmed_pilgrims_basic_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('confirmed_pilgrims_flight_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('confirmed_pilgrims_hotel_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('confirmed_pilgrims_transport_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('confirmed_pilgrims_ksa_part_data_submission', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')

def downgrade() -> None:
    op.drop_column('umrah_requisition', 'is_child_included_with_bed_transport', schema='core')
    op.drop_column('umrah_requisition', 'confirmed_remarks', schema='core')
    op.drop_column('umrah_requisition', 'confirmed_pilgrims_family_group', schema='core')
    op.drop_column('umrah_requisition', 'confirmed_pilgrims_basic_info', schema='core')
    op.drop_column('umrah_requisition', 'confirmed_pilgrims_flight_info', schema='core')
    op.drop_column('umrah_requisition', 'confirmed_pilgrims_transport_info', schema='core')
    op.drop_column('umrah_requisition', 'confirmed_pilgrims_ksa_part_data_submission', schema='core')
    op.drop_column('umrah_requisition', 'confirmed_pilgrims_hotel_info', schema='core')
    op.drop_column('umrah_requisition', 'reference', schema='core')