"""admin user is umrah assignee

Revision ID: b7e3c91d4a20
Revises: 9c2f4d7a1b6e
Create Date: 2026-10-01 17:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7e3c91d4a20'
down_revision: Union[str, Sequence[str], None] = '9c2f4d7a1b6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('admin_user',
                  sa.Column('is_umrah_assignee', sa.Boolean(), nullable=False, server_default=sa.false()),
                  schema='core')
    op.execute(
        "UPDATE core.admin_user SET is_umrah_assignee = true "
        "WHERE agency_name = 'Amin Travels & Tours' AND username IN ('tazwar', 'afnan', 'shahin')"
    )


def downgrade() -> None:
    op.drop_column('admin_user', 'is_umrah_assignee', schema='core')
