"""create admin table

Revision ID: ac42252c0b69
Revises: 337cd514413d
Create Date: 2025-07-31 15:24:56.007792

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ac42252c0b69'
down_revision: Union[str, Sequence[str], None] = '337cd514413d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('admin',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('user_name', sa.String(), nullable=False),
    sa.Column('profile_pic', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('role', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=False),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='core'
    )
    op.create_index(op.f('ix_core_admin_id'), 'admin', ['id'], unique=False, schema='core')

def downgrade() -> None:
    op.drop_index(op.f('ix_core_admin_id'), table_name='admin', schema='core')
    op.drop_table('admin', schema='core')
