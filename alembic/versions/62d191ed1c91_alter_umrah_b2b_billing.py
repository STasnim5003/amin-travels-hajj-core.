"""alter umrah b2b billing

Revision ID: 62d191ed1c91
Revises: 5ed75e22b5e2
Create Date: 2026-06-11 10:41:10.508089

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '62d191ed1c91'
down_revision: Union[str, Sequence[str], None] = '5ed75e22b5e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('umrah_b2b_payements', sa.Column('amin_office_code', sa.String(), nullable=False), schema='core')
    op.add_column('umrah_b2b_payements', sa.Column('amount', sa.FLOAT(), nullable=False), schema='core')
    op.drop_column('umrah_b2b_payements', 'bill', schema='core')
    op.drop_column('umrah_b2b_payements', 'credit', schema='core')
    op.drop_column('umrah_b2b_payements', 'b2b_agent_name', schema='core')
    op.drop_column('umrah_b2b_payements', 'guest_name', schema='core')
    op.drop_column('umrah_b2b_payements', 'sales_person', schema='core')
    op.drop_column('umrah_b2b_payements', 'description', schema='core')
    op.add_column('umrah_b2b_payements', sa.Column('description', sa.String(), nullable=True), schema='core')
    op.add_column('umrah_b2b_payements', sa.Column('b2b_agent_name', sa.String(), nullable=True), schema='core')
def downgrade() -> None:
    op.drop_column('umrah_b2b_payements', 'amin_office_code', schema='core')
    op.drop_column('umrah_b2b_payements', 'amount', schema='core')
