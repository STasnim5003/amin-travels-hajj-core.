"""alter admin table add lead agency

Revision ID: a69a9f9949d2
Revises: a2c3540f6f97
Create Date: 2025-10-25 12:39:29.719742

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a69a9f9949d2'
down_revision: Union[str, Sequence[str], None] = 'a2c3540f6f97'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('admin', sa.Column('lead_agency', sa.String(), nullable=True), schema="core")


def downgrade() -> None:
    op.drop_column('admin', 'lead_agency', schema="core")
