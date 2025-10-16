"""create table related to payment

Revision ID: 8a57cf29f09c
Revises: 27fce4fd6159
Create Date: 2025-10-16 11:44:29.569582

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a57cf29f09c'
down_revision: Union[str, Sequence[str], None] = '27fce4fd6159'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    # Create payment_category table
    op.create_table(
        'payment_category',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('agency_name', sa.String, nullable=False),
        sa.Column('created_at',sa.DateTime(),server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"),nullable=False),
        sa.Column('updated_at',sa.DateTime(),server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"),nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        schema='core'
    )
    op.create_index(
        op.f('ix_core_payment_category_id'),
        'payment_category',
        ['id'],
        unique=False,
        schema='core'
    )

    op.create_table(
        'package_name',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('agency_name', sa.String, nullable=False),
        sa.Column('created_at', sa.DateTime(),
                  server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=False),
        sa.Column('updated_at', sa.DateTime(),
                  server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        schema='core'
    )

    # Create bank_info table
    op.create_table(
        'bank_info',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('account_no', sa.String, nullable=True),
        sa.Column('branch', sa.String, nullable=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('agency_name', sa.String, nullable=False),
        sa.Column('created_at', sa.DateTime(),server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=False),
        sa.Column('updated_at', sa.DateTime(),server_default=sa.text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        schema='core'
    )
    op.create_index(
        op.f('ix_core_bank_info_id'),
        'bank_info',
        ['id'],
        unique=False,
        schema='core'
    )

    # Add new columns to payment table
    op.add_column('payment', sa.Column('bank_info_id', sa.Integer(), nullable=True), schema='core')
    op.add_column('payment', sa.Column('payment_category', sa.String(), nullable=True), schema='core')
    op.add_column('payment', sa.Column('way_of_payment', sa.String(), nullable=True), schema='core')

    # Optional: add foreign key constraint to bank_info if applicable
    op.create_foreign_key(
        'fk_payment_bank_info',
        'payment',
        'bank_info',
        ['bank_info_id'],
        ['id'],
        source_schema='core',
        referent_schema='core'
    )


def downgrade() -> None:
    # Drop foreign key if created
    op.drop_constraint('fk_payment_bank_info', 'payment', type_='foreignkey', schema='core')

    # Drop added columns from payment table
    op.drop_column('payment', 'way_of_payment', schema='core')
    op.drop_column('payment', 'payment_category', schema='core')
    op.drop_column('payment', 'bank_info_id', schema='core')

    # Drop bank_info table
    op.drop_index(op.f('ix_core_bank_info_id'), table_name='bank_info', schema='core')
    op.drop_table('bank_info', schema='core')

    # Drop payment_category table
    op.drop_index(op.f('ix_core_payment_category_id'), table_name='payment_category', schema='core')
    op.drop_table('payment_category', schema='core')

    op.drop_table('package_name', schema='core')