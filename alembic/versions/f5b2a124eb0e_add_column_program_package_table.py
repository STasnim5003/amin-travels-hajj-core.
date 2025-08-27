"""add column program & package table

Revision ID: f5b2a124eb0e
Revises: f6effa426859
Create Date: 2025-08-26 12:33:27.351980

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5b2a124eb0e'
down_revision: Union[str, Sequence[str], None] = 'f6effa426859'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("get_together_program_create", sa.Column("venue_address", sa.String(), nullable=True), schema="core")
    op.add_column("get_together_program_create", sa.Column("venue_map_location", sa.String(), nullable=True), schema="core")
    op.add_column("get_together_program_create", sa.Column("start_time", sa.String(), nullable=True), schema="core")
    op.add_column("get_together_program_create", sa.Column("program_type", sa.String(), nullable=True), schema="core")
    op.add_column("packages", sa.Column("discount_deadline", sa.Date(), nullable=True), schema="core")
    op.execute("""
                    UPDATE core.packages
                    SET discount_deadline = '2025-08-30'
                    WHERE hajj_month = 'October'
                      AND hajj_year = 2025
                      AND package_type = 'UMRAH'
                """)
    op.add_column("user_training_books", sa.Column("no_of_attendance", sa.Integer(), nullable=True), schema="core")


def downgrade() -> None:
    op.drop_column("get_together_program_create", "venue_map_location", schema="core")
    op.drop_column("get_together_program_create", "venue_address", schema="core")
    op.drop_column("get_together_program_create", "start_time", schema="core")
    op.drop_column("get_together_program_create", "program_type", schema="core")
    op.drop_column("packages", "discount_deadline", schema="core")
    op.drop_column("user_training_books", "no_of_attendance", schema="core")
