"""set sub agency amount

Revision ID: e302e6903a16
Revises: c7cf9c3f5d6e
Create Date: 2026-01-05 16:27:21.042825

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e302e6903a16'
down_revision: Union[str, Sequence[str], None] = 'c7cf9c3f5d6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE core.admin
            SET bdt = 0.0,
                sar = 0.0
            """
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
