"""pilgrim_package_flag_not_null

Revision ID: f1c4a9d2b7e3
Revises: e6b3f8a1c215
Create Date: 2026-10-14 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'f1c4a9d2b7e3'
down_revision: Union[str, Sequence[str], None] = 'e6b3f8a1c215'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# A NULL flag matches neither is_package_assigned=false nor =true, so the pilgrim drops out of
# both the unassigned list and /package-assigned-pilgrims. NULL means "no package", so backfill it.
def upgrade() -> None:
    op.execute("UPDATE core.pilgrim_data SET is_package_assigned = FALSE WHERE is_package_assigned IS NULL")
    op.execute("ALTER TABLE core.pilgrim_data ALTER COLUMN is_package_assigned SET DEFAULT FALSE")
    op.execute("ALTER TABLE core.pilgrim_data ALTER COLUMN is_package_assigned SET NOT NULL")


def downgrade() -> None:
    op.execute("ALTER TABLE core.pilgrim_data ALTER COLUMN is_package_assigned DROP NOT NULL")
