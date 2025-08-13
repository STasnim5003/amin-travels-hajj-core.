"""insert 2026 short package

Revision ID: f62d6ade1e73
Revises: 10b511c4c464
Create Date: 2025-08-14 01:19:43.880545

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f62d6ade1e73'
down_revision: Union[str, Sequence[str], None] = '10b511c4c464'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.execute("""
        INSERT INTO core.packages (
            id, name, discount, price, hajj_year, duration, description_type, package_type, hajj_month,
            others_feature, makkah, azizia, madinah, includes, hotel_info, excludes,
            created_at, updated_at, created_by, updated_by, is_active
        ) VALUES 
        (31,'Short Package',NULL,NULL,2026,17,'DETAILS','HAJJ',NULL,'["Duration: 16-17 Days", "Airlines: Saudi/Biman/Nas", "Flight Date: 1/2 - 16/17 Dhul Hijjah"]'::jsonb,
        '[ "Hotel: Elaf Kinda/ Makkah Tower/ Safa Tower/ Clock Tower or similar", "Distance: 100 meter (Haram)", "Duration: 6/7 days (After Hajj)", "Date: 1/2 - 5 Dhul Hijjah", "Room: 4 Bed" ]'::jsonb,
        '[ "Apartment", "Distance : Nearest to Jamarat", "Duration : 9/10 Days", "Date: 5 - 13/14 Dhul Hijja", "Room : 4-5 Bed"]'::jsonb,
        '[ "Hotel: Al Aqeeq/Movenpick/Pullman Zamam or similar", "Distance: 250 meter (Nabawi)",  "Hotel Type: 5 Star", "Duration: 4/5 days (After Hajj)", "Date: 13/14 - 16/17  Dhul Hijjah", "Room: 4 Bed" ]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        now(), now(),NULL,NULL,true),
        (32,'Short Package',NULL,NULL,2026,15,'DETAILS','HAJJ',NULL,'["Duration: 14-15 Days", "Airlines: Saudi/Biman/Nas", "Flight Date: 2/3 - 16/17 Dhul Hijjah"]'::jsonb,
        '[]'::jsonb,
        '[ "Apartment", "Distance : Nearest to Jamarat", "Duration : 9/10 Days", "Date: 2/3 - 13/14 Dhul Hijja", "Room : 4-5 Bed"]'::jsonb,
        '[ "Hotel: Al Aqeeq/Movenpick/Pullman Zamam or similar", "Distance: 250 meter (Nabawi)",  "Hotel Type: 5 Star", "Duration: 4/5 days (After Hajj)", "Date: 13/14 - 16/17  Dhul Hijjah", "Room: 4 Bed" ]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        now(), now(),NULL,NULL,true)
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM core.packages")

