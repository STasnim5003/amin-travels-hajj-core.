"""package_bed_type_json

Revision ID: e6b3f8a1c215
Revises: d5a7c2e9f041
Create Date: 2026-10-13 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e6b3f8a1c215'
down_revision: Union[str, Sequence[str], None] = 'd5a7c2e9f041'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# jsonb re-sorts object keys; json keeps the order the admin entered the room types in.
# Existing rows keep the order jsonb already gave them (the original order is not recoverable).
def upgrade() -> None:
    op.execute("ALTER TABLE core.packages ALTER COLUMN bed_type TYPE json USING bed_type::json")


def downgrade() -> None:
    op.execute("ALTER TABLE core.packages ALTER COLUMN bed_type TYPE jsonb USING bed_type::jsonb")
