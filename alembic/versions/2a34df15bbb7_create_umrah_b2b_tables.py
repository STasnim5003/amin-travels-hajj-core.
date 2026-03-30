"""create umrah b2b tables

Revision ID: 2a34df15bbb7
Revises: 1c532a2ff623
Create Date: 2026-03-30 13:49:32.261012

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '2a34df15bbb7'
down_revision: Union[str, Sequence[str], None] = '1c532a2ff623'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'umrah_b2b_agents',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, index=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('details', sa.String, nullable=True),
        sa.Column('total_bill', sa.BigInteger, nullable=False, server_default=sa.text('0')),
        sa.Column('total_due', sa.BigInteger, nullable=False, server_default=sa.text('0')),
        sa.Column('total_credit', sa.BigInteger, nullable=False, server_default=sa.text('0')),
        sa.Column('agency_name', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime(),
                  server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=False),
        sa.Column('updated_at', sa.DateTime(),
                  server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='core'
    )

    op.create_index(
        'ix_umrah_b2b_agents_name','umrah_b2b_agents',['name'], unique=True, schema='core'
    )

    op.create_table(
        'umrah_b2b_payements',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, index=True),
        sa.Column('b2b_agent_name', sa.String, nullable=False),
        sa.Column('guest_name', sa.String, nullable=False),
        sa.Column('description', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('way_of_payment', sa.String, nullable=True),
        sa.Column('bill', sa.BigInteger, nullable=False),
        sa.Column('credit', sa.BigInteger, nullable=False),
        sa.Column('payment_date', sa.Date, nullable=True),
        sa.Column('remarks', sa.String, nullable=True),
        sa.Column('agency_name', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime(),
                  server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=False),
        sa.Column('updated_at', sa.DateTime(),
                  server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='core'
    )

    op.create_index(
        'ix_umrah_b2b_agent_payments', 'umrah_b2b_payements', ['b2b_agent_name'], unique=False, schema='core'
    )
    op.create_index(
        'ix_umrah_b2b_agent_payment_date', 'umrah_b2b_payements', ['payment_date'], unique=False, schema='core'
    )


def downgrade() -> None:
    op.drop_index('ix_umrah_b2b_agents_name', table_name='umrah_b2b_agents', schema='core')
    op.drop_table('umrah_b2b_agents', schema='core')

    op.drop_index('ix_umrah_b2b_agent_payments', table_name='umrah_b2b_payements', schema='core')
    op.drop_index('ix_umrah_b2b_agent_payment_date', table_name='umrah_b2b_payements', schema='core')
    op.drop_table('umrah_b2b_payements', schema='core')