"""payment table indexing

Revision ID: 394995d5a8a1
Revises: d97a0e356590
Create Date: 2026-07-18 16:45:17.794405

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '394995d5a8a1'
down_revision: Union[str, Sequence[str], None] = 'd97a0e356590'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # Payment filtering index
    op.create_index(
        "idx_payment_agency_year_category",
        "payment",
        ["agency_name", "hajj_year", "category"],
        schema="core"
    )

    # Payment identifier indexes
    op.create_index(
        "idx_payment_tracking",
        "payment",
        ["tracking_id"],
        schema="core"
    )

    op.create_index(
        "idx_payment_nid",
        "payment",
        ["nid"],
        schema="core"
    )

    op.create_index(
        "idx_payment_passport",
        "payment",
        ["passport_no"],
        schema="core"
    )

    # Pilgrim lookup indexes
    op.create_index(
        "idx_pilgrim_tracking",
        "pilgrim_data",
        ["tracking_id"],
        schema="core"
    )

    op.create_index(
        "idx_pilgrim_nid",
        "pilgrim_data",
        ["nid"],
        schema="core"
    )

    op.create_index(
        "idx_pilgrim_passport",
        "pilgrim_data",
        ["passport_no"],
        schema="core"
    )


def downgrade() -> None:

    op.drop_index(
        "idx_payment_agency_year_category",
        table_name="payment",
        schema="core"
    )

    op.drop_index(
        "idx_payment_tracking",
        table_name="payment",
        schema="core"
    )

    op.drop_index(
        "idx_payment_nid",
        table_name="payment",
        schema="core"
    )

    op.drop_index(
        "idx_payment_passport",
        table_name="payment",
        schema="core"
    )

    op.drop_index(
        "idx_pilgrim_tracking",
        table_name="pilgrim_data",
        schema="core"
    )

    op.drop_index(
        "idx_pilgrim_nid",
        table_name="pilgrim_data",
        schema="core"
    )

    op.drop_index(
        "idx_pilgrim_passport",
        table_name="pilgrim_data",
        schema="core"
    )
