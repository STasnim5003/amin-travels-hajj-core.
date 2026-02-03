"""alter table admin user

Revision ID: 95a822c04fca
Revises: 9fb2aa8167a0
Create Date: 2026-02-03 12:42:39.138247

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql



# revision identifiers, used by Alembic.
revision: str = '95a822c04fca'
down_revision: Union[str, Sequence[str], None] = '9fb2aa8167a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('admin_user', sa.Column('hotel_name', sa.String(), nullable=True), schema='core')
    op.add_column('admin_user', sa.Column('others', sa.String(), nullable=True), schema='core')
    op.add_column('admin_user', sa.Column('ekama_file', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('admin_user', 'hotel_name', schema='core')
    op.drop_column('admin_user', 'ekama_file', schema='core')
    op.drop_column('admin_user', 'others', schema='core')
