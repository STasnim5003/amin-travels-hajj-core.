"""create hotel request

Revision ID: 85177ddf0249
Revises: 6ae77dd68566
Create Date: 2025-11-18 15:06:14.463463

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '85177ddf0249'
down_revision: Union[str, Sequence[str], None] = '6ae77dd68566'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('hotel_request',
    sa.Column('id', sa.Integer, autoincrement=True, primary_key=True, index=True),
        sa.Column('city', sa.String, nullable=False),
        sa.Column('type', sa.String, nullable=True),
        sa.Column('name', sa.String, nullable=True),
        sa.Column('tasria_number', sa.Integer, nullable=True),
        sa.Column('check_in', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('check_out', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('number_of_haji', sa.Integer, nullable=False),
        sa.Column('room_allocation', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('hotel_contact_person', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String, nullable=True),
        sa.Column('nusuk_request_id', sa.String, nullable=True),
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

def downgrade() -> None:
    op.drop_table('hotel_request', schema='core')
