"""insert packages third phase

Revision ID: 150d0c925d44
Revises: 9cdeed464d10
Create Date: 2025-08-13 04:59:28.722749

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '150d0c925d44'
down_revision: Union[str, Sequence[str], None] = '9cdeed464d10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO core.packages (
            id, name, discount, price, hajj_year, duration, description_type, package_type, hajj_month,
            others_feature, makkah, azizia, madinah, includes, hotel_info, excludes,
            created_at, updated_at, created_by, updated_by, is_active
        ) VALUES (25,'Luxury',NULL,NULL,2026,40,'SHORT','HAJJ',NULL,'[]'::jsonb,
        '[ "Hotel: 4/5 Star", "Distance: 100 meter (Haram)", "Room: 4-5 Bed" ]'::jsonb,
        '[ "Apartment", "Distance : 1.5 km (Mina) & 5/6 km (Haram)",  "Room: 4-5 Bed" ]'::jsonb,
        '[ "Hotel: 2/3 Star", "Distance: 300 meter (Nabawi)", "Room: 4-5 Bed" ]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        now(), now(),NULL,NULL,true),
        (26,'Standard',NULL,NULL,2026,40,'SHORT','HAJJ',NULL,'[]'::jsonb,
        '[ "Hotel: 2/3 Star", "Distance: 500-750 meter (Haram)", "Room: 5-6 Bed" ]'::jsonb,
        '[ "Apartment", "Distance : 1.5 km (Mina) & 5/6 km (Haram)",  "Room: 5-6 Bed" ]'::jsonb,
        '[ "Hotel: 2/3 Star", "Distance: 350-400 meter (Nabawi)", "Room: 5-6 Bed" ]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        now(), now(),NULL,NULL,true),
        (27,'Economy',NULL,NULL,2026,40,'SHORT','HAJJ',NULL,'[]'::jsonb,
        '[ "Hotel: Economt", "Distance: 900-1200 meter (Haram)", "Room: 5-7 Bed" ]'::jsonb,
        '[ "Normal Apartment", "Distance : 1.5 km (Mina) & 5/6 km (Haram)",  "Room: 5-7 Bed" ]'::jsonb,
        '[ "Hotel: Economy", "Distance: 550-850 meter (Nabawi)", "Room: 5-7 Bed" ]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        now(), now(),NULL,NULL,true)
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM core.packages")

