"""create training user table

Revision ID: 7e3336f2616a
Revises: ac42252c0b69
Create Date: 2025-08-12 13:30:52.174070

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e3336f2616a'
down_revision: Union[str, Sequence[str], None] = 'ac42252c0b69'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('user_training_books',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('whats_app_no', sa.String(), nullable=False),
    sa.Column('hajj_year', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=False),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='core'
    )
    op.create_index(op.f('ix_core_training_user_id'), 'user_training_books', ['id'], unique=False, schema='core')

def downgrade() -> None:
    op.drop_index(op.f('ix_core_training_user_id'), table_name='user_training_books', schema='core')
    op.drop_table('user_training_books', schema='core')
