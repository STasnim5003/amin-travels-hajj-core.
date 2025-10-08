"""alter admin user table

Revision ID: 3511ac302fa7
Revises: 529048b75c0b
Create Date: 2025-10-08 11:30:54.204294

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3511ac302fa7'
down_revision: Union[str, Sequence[str], None] = '529048b75c0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("pilgrim_data", sa.Column("total_payment", sa.Integer(), nullable=True, server_default="0"), schema='core')
    op.add_column("pilgrim_data", sa.Column("total_payable", sa.Integer(), nullable=True, server_default="0"), schema='core')
    op.add_column("pilgrim_data", sa.Column("reference", sa.String(), nullable=True), schema='core')
    op.add_column("pilgrim_data", sa.Column("group_leader", sa.String(), nullable=True), schema='core')
    op.add_column("admin_user", sa.Column("code", sa.String(), nullable=True), schema='core')
    op.add_column("admin_user", sa.Column("username", sa.String(), nullable=True), schema='core')
    op.add_column("admin_user", sa.Column("password", sa.String(), nullable=True), schema='core')
    op.create_table('payment',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('date', sa.String(), nullable=True),
        sa.Column('amount', sa.BigInteger(), nullable=True),
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
    op.create_index(op.f('ix_core_payment_id'), 'payment', ['id'], unique=False, schema='core')

def downgrade() -> None:
    op.drop_column("admin_user", "username", schema='core')
    op.drop_column("admin_user", "password", schema='core')
    op.drop_column("pilgrim_data", "group_leader", schema='core')
    op.drop_column("pilgrim_data", "total_payable", schema='core')
    op.drop_column("pilgrim_data", "total_payment", schema='core')
    op.drop_column("pilgrim_data", "reference", schema='core')
    op.drop_column("admin_user", "code", schema='core')
    op.drop_table('payment', schema='core')



