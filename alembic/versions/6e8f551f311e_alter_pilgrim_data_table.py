"""alter pilgrim data table

Revision ID: 6e8f551f311e
Revises: 0e9419b56cec
Create Date: 2026-05-11 16:17:00.651229

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e8f551f311e'
down_revision: Union[str, Sequence[str], None] = '0e9419b56cec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('pilgrim_data', sa.Column('remarks', sa.String(), nullable=True), schema='core')
    op.add_column('pilgrim_data', sa.Column('email', sa.String(), nullable=True), schema='core')
    op.add_column('pilgrim_data', sa.Column('interested_in_package', sa.String(), nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('pilgrim_data', 'remarks', schema = 'core')
    op.drop_column('pilgrim_data', 'email', schema = 'core')
    op.drop_column('pilgrim_data', 'interested_in_package', schema = 'core')
