"""add column training

Revision ID: 7d23a265ecb1
Revises: 6a5bd04dc765
Create Date: 2025-08-26 18:25:43.896962

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d23a265ecb1'
down_revision: Union[str, Sequence[str], None] = '6a5bd04dc765'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user_training_books", sa.Column("no_of_attendance", sa.Integer(), nullable=True), schema="core")



def downgrade() -> None:
    op.drop_column("user_training_books", "no_of_attendance", schema="core")

