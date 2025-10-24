"""alter pilgrim table add lead agency

Revision ID: a2c3540f6f97
Revises: f16a172ae350
Create Date: 2025-10-24 14:40:26.678755

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2c3540f6f97'
down_revision: Union[str, Sequence[str], None] = 'f16a172ae350'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('pilgrim_data', sa.Column('lead_agency', sa.String(), nullable=True), schema="core")
    op.add_column('pilgrim_data', sa.Column('sub_reference', sa.String(), nullable=True), schema="core")

def downgrade() -> None:
    op.drop_column('pilgrim_data', 'lead_agency', schema="core")
    op.drop_column('pilgrim_data', 'sub_reference', schema="core")
