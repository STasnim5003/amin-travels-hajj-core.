"""add mother agency

Revision ID: 2cb9e3a13835
Revises: e179926bc4e5
Create Date: 2026-08-06 13:22:55.981190

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2cb9e3a13835'
down_revision: Union[str, Sequence[str], None] = 'e179926bc4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("admin_user", sa.Column("mother_agency", sa.String(), nullable=True), schema="core")


def downgrade() -> None:
    op.drop_column("admin_user", "mother_agency", schema="core")
