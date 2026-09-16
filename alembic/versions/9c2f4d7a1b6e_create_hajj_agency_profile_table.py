"""create hajj agency profile table

Revision ID: 9c2f4d7a1b6e
Revises: 6aa3dfe8fea0
Create Date: 2026-09-16 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '9c2f4d7a1b6e'
down_revision: Union[str, Sequence[str], None] = '6aa3dfe8fea0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'hajj_agency_profile',
        sa.Column('hl', sa.String(10), nullable=False),
        sa.Column('sl_no', sa.Integer, nullable=True),
        sa.Column('agency_name', sa.String(255), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('address', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('pre_reg', sa.Integer, nullable=True),
        sa.Column('reg', sa.Integer, nullable=True),
        sa.Column('total', sa.Integer, nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text("(NOW() AT TIME ZONE 'Asia/Dhaka')"), nullable=True),
        sa.PrimaryKeyConstraint('hl'),
        schema='core'
    )


def downgrade() -> None:
    op.drop_table('hajj_agency_profile', schema='core')
