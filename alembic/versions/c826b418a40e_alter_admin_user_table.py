"""alter admin user table

Revision ID: c826b418a40e
Revises: 68cb37733a7c
Create Date: 2026-02-27 14:19:02.218949

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c826b418a40e'
down_revision: Union[str, Sequence[str], None] = '68cb37733a7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('admin_user', sa.Column('nid', sa.String(), nullable=True), schema='core')
    op.add_column('admin_user', sa.Column('tracking_id', sa.String(), nullable=True), schema='core')
    op.add_column('admin_user', sa.Column('dob', sa.String(), nullable=True), schema='core')
    op.add_column('admin_user', sa.Column('ksa_mobile', sa.String(), nullable=True), schema='core')
    op.add_column('admin_user', sa.Column('gender', sa.String(), nullable=True), schema='core')


def downgrade() -> None:
    op.drop_column('admin_user', 'dob', schema='core')
    op.drop_column('admin_user', 'ksa_mobile', schema='core')
    op.drop_column('admin_user', 'tracking_id', schema='core')
    op.drop_column('admin_user', 'nid', schema='core')
    op.drop_column('admin_user', 'gender', schema='core')
