"""admin_document_profile

Revision ID: d5a7c2e9f041
Revises: c4d8e1a7b932
Create Date: 2026-10-05 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'd5a7c2e9f041'
down_revision: Union[str, Sequence[str], None] = 'c4d8e1a7b932'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Letterhead / signing details printed on receipts, invoices and umrah requests.
TEXT_COLUMNS = ['agency_name_bn', 'umrah_license_number', 'address', 'office_phone', 'office_email', 'website',
                'signatory_name', 'signatory_designation']
JSONB_COLUMNS = ['billing_contact', 'bank_accounts', 'signature', 'seal']


def upgrade() -> None:
    for name in TEXT_COLUMNS:
        op.add_column('admin', sa.Column(name, sa.Text(), nullable=True), schema='core')
    for name in JSONB_COLUMNS:
        op.add_column('admin', sa.Column(name, JSONB(), nullable=True), schema='core')


def downgrade() -> None:
    for name in TEXT_COLUMNS + JSONB_COLUMNS:
        op.drop_column('admin', name, schema='core')
