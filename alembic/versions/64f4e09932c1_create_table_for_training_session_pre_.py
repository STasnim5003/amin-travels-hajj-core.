"""create table for training session & pre register equiry

Revision ID: 64f4e09932c1
Revises: 26b038c0d3cf
Create Date: 2026-06-18 15:51:10.422564

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '64f4e09932c1'
down_revision: Union[str, Sequence[str], None] = '26b038c0d3cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('book_training_session_and_pre_register_customer',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, index=True),
        sa.Column('name_en', sa.String, nullable=False),
        sa.Column('father_name', sa.String, nullable=True),
        sa.Column('mobile_no', sa.String, nullable=False),
        sa.Column('email', sa.String, nullable=True),
        sa.Column('interested_in_package', sa.String, nullable=True),
        sa.Column('remarks', sa.String, nullable=True),
        sa.Column('number_of_people', sa.Integer, nullable=True),
        sa.Column('media', sa.String, nullable=True),
        sa.Column('purpose', sa.String, nullable=True),
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
        sa.PrimaryKeyConstraint('id'),
        schema='core'
    )


def downgrade() -> None:
    op.drop_table('book_training_session_and_pre_register_customer', schema='core')
