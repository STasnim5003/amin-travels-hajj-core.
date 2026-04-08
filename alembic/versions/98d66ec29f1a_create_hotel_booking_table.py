"""create hotel booking table

Revision ID: 98d66ec29f1a
Revises: aef096f89d52
Create Date: 2026-04-08 15:12:29.606009

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '98d66ec29f1a'
down_revision: Union[str, Sequence[str], None] = 'aef096f89d52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('umrah_hotel_booking',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('res_no', sa.String, nullable=False),
        sa.Column('guest_name', sa.String, nullable=False),
        sa.Column('hotel_name', sa.String, nullable=False),
        sa.Column('room_type', sa.String, nullable=True),
        sa.Column('mp', sa.String, nullable=True),
        sa.Column('qty', sa.String, nullable=True),
        sa.Column('check_in', sa.String, nullable=True),
        sa.Column('check_out', sa.String, nullable=True),
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

    op.add_column('umrah_requisition', sa.Column('emergency_contract_person', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')


def downgrade() -> None:
    op.drop_table('umrah_hotel_booking', schema='core')
    op.drop_column('umrah_requisition', 'emergency_contract_person',schema='core')
