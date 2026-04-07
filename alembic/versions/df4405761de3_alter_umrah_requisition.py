"""alter umrah requisition 

Revision ID: df4405761de3
Revises: d6e6646fab04
Create Date: 2026-04-07 15:00:03.533864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df4405761de3'
down_revision: Union[str, Sequence[str], None] = 'd6e6646fab04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('umrah_requisition', 'umrah_requisition_code', schema='core')
    op.drop_column('umrah_customer_billing', 'umrah_requisition_code', schema='core')
    op.drop_column('umrah_vendor_billing', 'umrah_requisition_code', schema='core')

    op.add_column('umrah_requisition', sa.Column('amin_office_code', sa.Text(), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('discount', sa.Float(), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('requisition_type', sa.Text(), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('b2b_agent_name', sa.Text(), nullable=True), schema='core')
    op.add_column('umrah_requisition', sa.Column('sales_person', sa.Text(), nullable=True), schema='core')

    op.add_column('umrah_customer_billing', sa.Column('amin_office_code', sa.Text(), nullable=True), schema='core')
    op.add_column('umrah_vendor_billing', sa.Column('amin_office_code', sa.Text(), nullable=True), schema='core')

    op.drop_column('umrah_requisition', 'invoice_no', schema='core')
    op.create_index(
        'ix_umrah_requisition_amin_office_code',
        'umrah_requisition',
        ['amin_office_code'],
        unique=False,
        schema='core'
    )
    op.create_index(
        'ix_umrah_requisition_amin_office_code_vendor_billing',
        'umrah_vendor_billing',
        ['amin_office_code'],
        unique=False,
        schema='core'
    )
    op.create_index(
        'ix_umrah_requisition_amin_office_code_customer_billing',
        'umrah_customer_billing',
        ['amin_office_code'],
        unique=False,
        schema='core'
    )

    op.create_index(
        'ix_umrah_requisition_b2b_agent_name',
        'umrah_requisition',
        ['b2b_agent_name'],
        unique=False,
        schema='core'
    )

    op.execute("""
    CREATE SEQUENCE core.amin_office_seq
    START 1
    MINVALUE 1
    NO MAXVALUE
    CACHE 1;
    """)

def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_umrah_requisition_amin_office_code', table_name='umrah_requisition', schema='core')
    op.drop_index('ix_umrah_requisition_b2b_agent_name', table_name='umrah_requisition', schema='core')
    op.drop_index('ix_umrah_requisition_amin_office_code_customer_billing', table_name='umrah_customer_billing', schema='core')
    op.drop_index('ix_umrah_requisition_amin_office_code_vendor_billing', table_name='umrah_vendor_billing', schema='core')

    # Drop added columns
    op.drop_column('umrah_requisition', 'amin_office_code', schema='core')
    op.drop_column('umrah_customer_billing', 'amin_office_code', schema='core')
    op.drop_column('umrah_vendor_billing', 'amin_office_code', schema='core')
    op.drop_column('umrah_requisition', 'discount', schema='core')
    op.drop_column('umrah_requisition', 'requisition_type', schema='core')
    op.drop_column('umrah_requisition', 'b2b_agent_name', schema='core')
    op.drop_column('umrah_requisition', 'sales_person', schema='core')
    op.execute("DROP SEQUENCE IF EXISTS core.amin_office_seq;")