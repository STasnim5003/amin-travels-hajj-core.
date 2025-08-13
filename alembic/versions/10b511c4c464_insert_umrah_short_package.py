"""insert umrah short package

Revision ID: 10b511c4c464
Revises: 150d0c925d44
Create Date: 2025-08-13 05:03:30.254028

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '10b511c4c464'
down_revision: Union[str, Sequence[str], None] = '150d0c925d44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO core.packages (
            id, name, discount, price, hajj_year, duration, description_type, package_type, hajj_month,
            others_feature, makkah, azizia, madinah, includes, hotel_info, excludes,
            created_at, updated_at, created_by, updated_by, is_active
        ) VALUES (28,'Economy',NULL,135000,2025,NULL,'DETAILS','UMRAH','September','[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '["Umrah Visa", "Transit Flight Tickets (Dhaka-Jeddah-Madinah-Dhaka", "Jeddah-Makkah-Madinah-Airport Transport", "Hotel Accomodation", "Umrah Guide Service", "Ground Support Staff", "Makkah-Madinah Jiyarah"]'::jsonb,
        '[{"Makkah": ["Duration 800-1000 meter", "Hotel Al Wafidin/similar", "Room Type 5-6 Shared"]}, {"Madinah": ["Duration : 450-500 meter", "Miramar Hotel/Similar", "Room Type 5-6 Shared"]}]'::jsonb,
        '["All Category Food", "Any Type of Personal Expenses", "Zamzam Water", "Jeddah-Tayef-Badr & Any Tour is Not Included in this Package"]'::jsonb,
        now(), now(),NULL,NULL,true),
        (29,'Short Package',NULL,970000,2025,17,'DETAILS','HAJJ',NULL,'["Duration: 16-17 Days", "Airlines: Saudi/Biman/Nas", "Flight Date: 1/2 - 16/17 Dhul Hijjah"]'::jsonb,
        '[ "Hotel: Elaf Kinda/ Makkah Tower/ Safa Tower/ Clock Tower or similar", "Distance: 100 meter (Haram)", "Duration: 6/7 days (After Hajj)", "Date: 1/2 - 5 Dhul Hijjah", "Room: 4 Bed" ]'::jsonb,
        '[ "Apartment", "Distance : Nearest to Jamarat", "Duration : 9/10 Days", "Date: 5 - 13/14 Dhul Hijja", "Room : 4-5 Bed"]'::jsonb,
        '[ "Hotel: Al Aqeeq/Movenpick/Pullman Zamam or similar", "Distance: 250 meter (Nabawi)",  "Hotel Type: 5 Star", "Duration: 4/5 days (After Hajj)", "Date: 13/14 - 16/17  Dhul Hijjah", "Room: 4 Bed" ]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        now(), now(),NULL,NULL,true),
        (30,'Short Package',NULL,775000,2025,15,'DETAILS','HAJJ',NULL,'["Duration: 14-15 Days", "Airlines: Saudi/Biman/Nas", "Flight Date: 2/3 - 16/17 Dhul Hijjah"]'::jsonb,
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

