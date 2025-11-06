"""create table flight & zone request

Revision ID: 7d581a1abd21
Revises: 4598d3ca0c6f
Create Date: 2025-11-06 13:44:01.342014

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7d581a1abd21'
down_revision: Union[str, Sequence[str], None] = '4598d3ca0c6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'flight_request',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, index=True),
        sa.Column('total_seat', sa.Integer, nullable=False),
        sa.Column('flight_name', sa.String, nullable=False),
        sa.Column('arrival_route', sa.String, nullable=False),
        sa.Column('arrival_date_option_1', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('arrival_date_option_2', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('departure_route', sa.String, nullable=False),
        sa.Column('departure_date_option_1', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('departure_date_option_2', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
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

    op.create_table('zone_request',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, index=True),
        sa.Column('agency_name', sa.String, nullable=False),
        sa.Column('zone_wise_tent_in_mina', sa.String, nullable=True),
        sa.Column('zone_wise_pilgrims', sa.Integer, nullable=True),
        sa.Column('service_company_in_mina_arafat', sa.String, nullable=True),
        sa.Column('package_in_mina_arafat', sa.String, nullable=True),
        sa.Column('remarks', sa.String, nullable=True),
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


def downgrade() -> None:
    op.drop_table('flight_request', schema='core')
    op.drop_table('zone_request', schema='core')