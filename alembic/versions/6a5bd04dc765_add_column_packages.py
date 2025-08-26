"""add column packages

Revision ID: 6a5bd04dc765
Revises: f5b2a124eb0e
Create Date: 2025-08-26 16:32:54.040420

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a5bd04dc765'
down_revision: Union[str, Sequence[str], None] = 'f5b2a124eb0e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("packages", sa.Column("discount_deadline", sa.Date(), nullable=True), schema="core")
    op.execute("""
                UPDATE core.packages
                SET discount_deadline = '2025-08-30'
                WHERE hajj_month = 'October'
                  AND hajj_year = 2025
                  AND package_type = 'UMRAH'
            """)

def downgrade() -> None:
    op.drop_column("packages", "discount_deadline", schema="core")

