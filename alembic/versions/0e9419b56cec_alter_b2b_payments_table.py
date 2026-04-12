"""alter b2b payments table

Revision ID: 0e9419b56cec
Revises: 56ce53c3b3b6
Create Date: 2026-04-12 14:30:46.316763

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e9419b56cec'
down_revision: Union[str, Sequence[str], None] = '56ce53c3b3b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('umrah_b2b_payements',sa.Column('sales_person',sa.String(),nullable=True,),schema="core")


def downgrade() -> None:
    op.drop_column('umrah_b2b_payements','sales_person',schema="core")
