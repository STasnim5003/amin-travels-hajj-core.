"""alter umrah requisition

Revision ID: e4398662db5c
Revises: 25403462e2dd
Create Date: 2026-07-06 15:54:02.818692

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4398662db5c'
down_revision: Union[str, Sequence[str], None] = '25403462e2dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("umrah_requisition","name", existing_type=sa.String(), nullable=True,schema='core')
    op.alter_column("umrah_requisition","air_ticket", existing_type=sa.String(), nullable=True,schema='core')

    op.alter_column(
        "umrah_requisition",
        "is_visa",
        existing_type=sa.String(),
        nullable=True,
        schema='core'
    )

    op.alter_column(
        "umrah_requisition",
        "hotel_info",
        existing_type=sa.String(),
        nullable=True,
        schema='core'
    )

    op.alter_column(
        "umrah_requisition",
        "transport",
        existing_type=sa.String(),
        nullable=True,
        schema='core'
    )


def downgrade() -> None:
    op.alter_column(
        "umrah_requisition",
        "name",
        existing_type=sa.String(),
        nullable=False,
        schema='core'
    )

    op.alter_column(
        "umrah_requisition",
        "is_visa",
        existing_type=sa.String(),
        nullable=False,
        schema='core'
    )

    op.alter_column(
        "umrah_requisition",
        "hotel_info",
        existing_type=sa.String(),
        nullable=False,
        schema='core'
    )

    op.alter_column("umrah_requisition","transport",existing_type=sa.String(),nullable=False, schema='core')
    op.alter_column("umrah_requisition","air_ticket",existing_type=sa.String(),nullable=False, schema='core')
