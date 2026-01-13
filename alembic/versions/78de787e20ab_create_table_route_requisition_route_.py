"""create table route requisition & route dependency

Revision ID: 78de787e20ab
Revises: 2c1825683c0a
Create Date: 2026-01-13 14:23:53.418636

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '78de787e20ab'
down_revision: Union[str, Sequence[str], None] = '2c1825683c0a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'routes_for_requisition',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, index=True),
        sa.Column('route_type', sa.String, nullable=False),
        sa.Column('route_name', sa.String, nullable=False),
        sa.Column('route_price', sa.Float, nullable=False),
        sa.Column('route_mapping_id', sa.String, nullable=False),
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

    op.create_table(
        'route_request',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, index=True),
        sa.Column('route_type', sa.String, nullable=False),
        sa.Column('route_name', sa.String, nullable=False),
        sa.Column('route_price', sa.Float, nullable=False),
        sa.Column('number_of_pax', sa.Integer, nullable=False),
        sa.Column('total_price', sa.Float, nullable=False),
        sa.Column('agency_name', sa.String, nullable=True),
        sa.Column('status', sa.String, nullable=True),
        sa.Column('cancellation_status', sa.String, nullable=True),
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


def downgrade() -> None:
    op.drop_table('routes_for_requisition', schema='core')
    op.drop_table('route_request', schema='core')
