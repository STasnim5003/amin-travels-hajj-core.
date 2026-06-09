"""create family group code

Revision ID: 5ed75e22b5e2
Revises: 6e8f551f311e
Create Date: 2026-06-09 15:55:46.897975

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ed75e22b5e2'
down_revision: Union[str, Sequence[str], None] = '6e8f551f311e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create sequence in core schema
    op.execute("""
    CREATE SEQUENCE core.fg_code_seq START 101
    """)

    # Set default value for column
    op.execute("""
    ALTER TABLE core.umrah_requisition
    ALTER COLUMN confirmed_pilgrims_family_group
    SET DEFAULT ('FG-' || nextval('core.fg_code_seq'))
    """)


def downgrade() -> None:
    op.execute("""
    ALTER TABLE core.umrah_requisition
    ALTER COLUMN confirmed_pilgrims_family_group
    DROP DEFAULT
    """)

    op.execute("DROP SEQUENCE IF EXISTS core.fg_code_seq")
