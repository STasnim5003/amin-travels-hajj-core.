"""alter packages table

Revision ID: 1780fe29a48a
Revises: e4398662db5c
Create Date: 2026-07-08 13:15:20.691344

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1780fe29a48a'
down_revision: Union[str, Sequence[str], None] = 'e4398662db5c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('packages', sa.Column('air_ticket', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('packages', sa.Column('transportation', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('packages', sa.Column('mina_and_arafah', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('packages', sa.Column('hajj_guide', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('packages', sa.Column('qurbani', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('packages', sa.Column('tayef_jeddah_ziyara', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('packages', sa.Column('additional_services', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('packages', sa.Column('important_notes', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')
    op.add_column('packages', sa.Column('required_add_ons', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')

def downgrade() -> None:
    op.drop_column('packages', 'air_ticket', schema='core')
    op.drop_column('packages', 'transportation', schema='core')
    op.drop_column('packages', 'mina_and_arafah', schema='core')
    op.drop_column('packages', 'hajj_guide', schema='core')
    op.drop_column('packages', 'qurbani', schema='core')
    op.drop_column('packages', 'tayef_jeddah_ziyara', schema='core')
    op.drop_column('packages', 'additional_services', schema='core')
    op.drop_column('packages', 'important_notes', schema='core')
    op.drop_column('packages', 'required_add_ons', schema='core')
