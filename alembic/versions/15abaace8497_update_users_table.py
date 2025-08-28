"""update_users_table

Revision ID: 15abaace8497
Revises: f5b2a124eb0e
Create Date: 2025-08-28 15:08:30.521412

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '15abaace8497'
down_revision: Union[str, Sequence[str], None] = 'f5b2a124eb0e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column('passport_images', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema="core")
    op.add_column("users", sa.Column('vaccine_center', sa.String(), nullable=True), schema="core")
    op.add_column("users", sa.Column('registration_status', sa.String(), nullable=False, server_default="PREREGISTERED"), schema="core")
    op.add_column("users", sa.Column('username', sa.String(), index=True, nullable=True), schema="core")
    op.add_column("users", sa.Column('password', sa.String(), nullable=True), schema="core")
    op.add_column("users", sa.Column('role', sa.String(), nullable=False, server_default="PREREGISTERED_USER"), schema="core")



    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "role", schema="core")
    op.drop_column("users", "password", schema="core")
    op.drop_column("users", "username", schema="core")
    op.drop_column("users", "registration_status", schema="core")
    op.drop_column("users", "vaccine_center", schema="core")
    op.drop_column("users", "passport_images", schema="core")

    pass
