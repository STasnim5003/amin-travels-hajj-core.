"""create get together tables

Revision ID: 5c6278cf49a4
Revises: f62d6ade1e73
Create Date: 2025-08-20 13:59:46.369079

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5c6278cf49a4'
down_revision: Union[str, Sequence[str], None] = 'f62d6ade1e73'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('get_together_program_create',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('program_date', sa.DATE(), nullable=True),
    sa.Column('registration_deadline', sa.DATE(), nullable=True),
    sa.Column('program_venue', sa.String(), nullable=True),
    sa.Column('total_seat', sa.Integer(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(),
              server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"),
              nullable=False),
    sa.Column('updated_at', sa.DateTime(),
              server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"),
              nullable=False),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='core'
    )
    op.create_index(op.f('ix_core_get_together_program_id'), 'get_together_program_create', ['id'], unique=False, schema='core')

    op.create_table('get_together_registration',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('phone_no', sa.String(), nullable=False),
    sa.Column('no_of_attendance', sa.Integer(), nullable=False),
    sa.Column('get_together_program_id', sa.BigInteger(), nullable=False),
    sa.Column('created_at', sa.DateTime(),
              server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"),
              nullable=False),
    sa.Column('updated_at', sa.DateTime(),
              server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"),
              nullable=False),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.ForeignKeyConstraint(['get_together_program_id'], ['core.get_together_program_create.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='core'
    )
    op.create_index(op.f('ix_core_get_together_registration_id'), 'get_together_registration', ['id'], unique=False, schema='core')


def downgrade() -> None:
    op.drop_index(op.f('ix_core_get_together_program_id'), table_name='get_together_program_create', schema='core')
    op.drop_table('get_together_program_create', schema='core')
    op.drop_index(op.f('ix_core_get_together_registration_id'), table_name='get_together_registration', schema='core')
    op.drop_table('get_together_registration', schema='core')
