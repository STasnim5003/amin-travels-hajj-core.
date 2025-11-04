"""alter pilgrim table add sub_group

Revision ID: 4598d3ca0c6f
Revises: 69f8f291f707
Create Date: 2025-11-04 15:10:30.493470

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4598d3ca0c6f'
down_revision: Union[str, Sequence[str], None] = '69f8f291f707'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('pilgrim_data', sa.Column('sub_group', sa.String(), nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('pilgrim_data', 'sub_group', schema='core')
