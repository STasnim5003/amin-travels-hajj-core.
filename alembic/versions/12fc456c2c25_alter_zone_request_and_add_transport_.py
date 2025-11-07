"""alter zone_request and add transport data

Revision ID: 12fc456c2c25
Revises: 8316b73296a4
Create Date: 2025-11-07 15:41:29.610692

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12fc456c2c25'
down_revision: Union[str, Sequence[str], None] = '8316b73296a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('zone_request', sa.Column('total_pilgrims', sa.Integer, nullable=True), schema='core')

    op.create_table('transport_service',
    sa.Column('id', sa.Integer, autoincrement=True, index = True,nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('seats', sa.String, nullable=False),
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

    op.create_table('city_name',
        sa.Column('id', sa.Integer, autoincrement=True, index=True ,nullable=False),
        sa.Column('name', sa.String, nullable=False),
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
    op.drop_column('zone_request', 'total_pilgrims', schema='core')
    op.drop_table('transport_service', schema='core')
    op.drop_table('city_name', schema='core')
