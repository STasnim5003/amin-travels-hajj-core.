"""pilgrim_second_nationality

Revision ID: a7d2c9e4f1b8
Revises: f1c4a9d2b7e3
Create Date: 2026-10-14 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a7d2c9e4f1b8'
down_revision: Union[str, Sequence[str], None] = 'f1c4a9d2b7e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# PRP's "Second Nationality"; filled in only for NRB (Non-Resident Bangladeshi) pilgrims.
# The scraper writes this column, so this must be applied before the scraper is deployed.
def upgrade() -> None:
    # adding a nullable column is instant, but it needs a brief exclusive lock; fail fast rather than
    # queue behind a long query and block the live app's reads on pilgrim_data meanwhile
    op.execute("SET LOCAL lock_timeout = '5s'")
    op.execute("ALTER TABLE core.pilgrim_data ADD COLUMN IF NOT EXISTS second_nationality VARCHAR")


def downgrade() -> None:
    op.execute("ALTER TABLE core.pilgrim_data DROP COLUMN IF EXISTS second_nationality")
