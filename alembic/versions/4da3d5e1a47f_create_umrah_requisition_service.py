"""create umrah requisition service

Revision ID: 4da3d5e1a47f
Revises: 92a20b783b3c
Create Date: 2025-11-12 17:16:35.494727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4da3d5e1a47f'
down_revision: Union[str, Sequence[str], None] = '92a20b783b3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('umrah_requisition', sa.Column('ziara', sa.Boolean, nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('per_head_price_adult', sa.BigInteger, nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('per_head_price_child', sa.BigInteger, nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('per_head_price_infant', sa.BigInteger, nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('total_vendor_price', sa.BigInteger, nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('total_service_charge', sa.BigInteger, nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('total_price', sa.BigInteger, nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('visa_price', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('air_ticket_price', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('train_price', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('ziara_price', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('guide_price', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('food_price', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('others_price', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('is_confirmed', sa.Boolean, nullable=True), schema='core')

def downgrade() -> None:
    op.drop_column('umrah_requisition', 'others_price', schema='core')
    op.drop_column('umrah_requisition', 'food_price', schema='core')
    op.drop_column('umrah_requisition', 'guide_price', schema='core')
    op.drop_column('umrah_requisition', 'ziara_price', schema='core')
    op.drop_column('umrah_requisition', 'train_price', schema='core')
    op.drop_column('umrah_requisition', 'air_ticket_price', schema='core')
    op.drop_column('umrah_requisition', 'visa_price', schema='core')
    op.drop_column('umrah_requisition', 'total_price', schema='core')
    op.drop_column('umrah_requisition', 'total_service_charge', schema='core')
    op.drop_column('umrah_requisition', 'total_vendor_price', schema='core')
    op.drop_column('umrah_requisition', 'per_head_price_infant', schema='core')
    op.drop_column('umrah_requisition', 'per_head_price_child', schema='core')
    op.drop_column('umrah_requisition', 'per_head_price_adult', schema='core')
    op.drop_column('umrah_requisition', 'ziara', schema='core')
    op.drop_column('umrah_requisition', 'is_confirmed', schema='core')