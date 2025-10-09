"""alter pilgrim table add coloumn

Revision ID: 5e39aa0d2bb4
Revises: 1bd62b0bc74c
Create Date: 2025-10-09 16:04:57.554486

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e39aa0d2bb4'
down_revision: Union[str, Sequence[str], None] = '1bd62b0bc74c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('pilgrim_data', sa.Column('is_package_assigned', sa.Boolean(), nullable=True, server_default=sa.text('false')), schema='core')


def downgrade() -> None:
    op.drop_column('pilgrim_data', 'is_package_assigned', schema='core')
