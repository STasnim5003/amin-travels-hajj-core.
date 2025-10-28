"""alter pilgrim table

Revision ID: 69f8f291f707
Revises: 45b5a63a2e68
Create Date: 2025-10-28 16:17:02.536435

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '69f8f291f707'
down_revision: Union[str, Sequence[str], None] = '45b5a63a2e68'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("pilgrim_data", sa.Column("family_code", sa.String(), nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('pilgrim_data', 'family_code', schema='core')
