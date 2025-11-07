"""create umrah requisition table

Revision ID: 8316b73296a4
Revises: 7d581a1abd21
Create Date: 2025-11-07 11:58:54.105278

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8316b73296a4'
down_revision: Union[str, Sequence[str], None] = '7d581a1abd21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('umrah_requisition',
    sa.Column('id', sa.Integer, autoincrement=True, primary_key=True, index=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('number_of_traveller', sa.Integer, nullable=False),
        sa.Column('adult_traveller', sa.Integer, nullable=False),
        sa.Column('other_traveller', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_visa', sa.Boolean, nullable=False),
        sa.Column('with_hotel_brn', sa.Boolean, nullable=True),
        sa.Column('air_ticket', sa.Boolean, nullable=False),
        sa.Column('air_ticket_category', sa.String, nullable=True),
        sa.Column('airline_preference', sa.String, nullable=True),
        sa.Column('flight_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('hotel_info', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('transport', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('remarks', sa.String, nullable=True),
        sa.Column('agency_name', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime(),
                  server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"),
                  nullable=False),
        sa.Column('updated_at', sa.DateTime(),
                  server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"),
                  nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        schema='core'
    )

    op.drop_column('flight_request', 'arrival_route',schema='core')
    op.drop_column('flight_request', 'departure_route',schema='core')

    op.add_column('flight_request', sa.Column('arrival_route', sa.Integer), schema='core')
    op.add_column('flight_request', sa.Column('departure_route', sa.Integer), schema='core')




def downgrade() -> None:
    op.drop_table('umrah_requisition', schema='core')
