"""alter hotel request table

Revision ID: 7016c45b60c4
Revises: da1a40053a4d
Create Date: 2026-01-12 15:07:20.269832

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '7016c45b60c4'
down_revision: Union[str, Sequence[str], None] = 'da1a40053a4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('hotel_request', sa.Column('tasria_copy', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('hotel_request', 'tasria_copy', schema='core')
