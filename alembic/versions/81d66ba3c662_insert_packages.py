"""insert packages

Revision ID: 81d66ba3c662
Revises: 337cd514413d
Create Date: 2025-08-13 02:34:15.242051

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '81d66ba3c662'
down_revision: Union[str, Sequence[str], None] = '337cd514413d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO core.packages (
    id, name, discount, price, hajj_year, duration, description_type, package_type, hajj_month,
    others_feature, makkah, azizia, madinah, includes, hotel_info, excludes,
    created_at, updated_at, created_by, updated_by, is_active
) VALUES (1,'Exclusive',NULL,1135000,2025,40,'DETAILS','HAJJ',NULL,'[ "Duration: 40-43 Days", "Airlines: Saudi/Biman/Nas", "Flight Date: 5/7 Dhul Qadah - 17/19 Dhul Hijjah" ]'::jsonb,
    '[ "Hotel: Elaf Kinda/Makkah Tower/Safa Tower or similar", "Distance: 100 meter (Haram)", "Hotel Type: 5 Star", "Duration: 18/20 days (Before Hajj)", "Date: 5/7 - 25 Dhul Qadah", "Room: 4 Bed" ]'::jsonb,
    '[ "Apartment", "Distance : Nearest to Jamarat", "Duration : 10/12 Days", "Date: 5/7 Dhul Hijja & 10-17/19 Dhul Hijja", "Room : 4 Bed" ]'::jsonb,
    '[ "Hotel: Al Aqeeq/Movenpick/Pullman Zamam or similar", "Distance: 150 meter (Nabawi)", "Hotel Type: 5 Star", "Duration: 9 days (Befre Hajj)", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 4 Bed" ]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    now(), now(),NULL,NULL,true),
    (2,'Exclusive',NULL,1115000,2025,30,'DETAILS','HAJJ',NULL,'[ "Duration: 28-32 Days", "Airlines: Saudi/Biman/Nas", "Flight Date: 15/18 Dhul Qadah - 25 Dhul Hijjah" ]'::jsonb,
    '[ "Hotel: Elaf Kinda/Makkah Tower/Safa Tower or similar", "Distance: 100 meter (Haram)", "Hotel Type: 5 Star", "Duration: 10/7 days (Before Hajj)", "Date: 15/18 - 25 Dhul Qadah", "Room: 4 Bed" ]'::jsonb,
    '[ "Apartment", "Distance : Nearest to Jamarat", "Duration : 10/12 Days", "Date: 5/7 Dhul Hijja & 10-17/19 Dhul Hijja", "Room : 4 Bed" ]'::jsonb,
    '[ "Hotel: Al Aqeeq/Movenpick/Pullman Zamam or similar", "Distance: 150 meter (Nabawi)", "Hotel Type: 5 Star", "Duration: 8/9 days (Befre Hajj)", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 4 Bed" ]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    now(), now(),NULL,NULL,true),
    (3,'Exclusive',NULL,1015000,2025,20,'DETAILS','HAJJ',NULL,'[ "Duration: 20-24 Days", "Airlines: Saudi/Biman/Nas" ]'::jsonb,
    '[]'::jsonb,
    '[ "Apartment", "Distance : Nearest to Jamarat", "Duration : 10/12 Days", "Date: 5/7 Dhul Hijja & 10-17/19 Dhul Hijja", "Room : 4 Bed" ]'::jsonb,
    '[ "Hotel: Al Aqeeq/Movenpick/Pullman Zamam or similar", "Distance: 150 meter (Nabawi)", "Hotel Type: 5 Star", "Duration: 8/9 days (Befre Hajj)", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 4 Bed" ]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    now(), now(),NULL,NULL,true),
    (4,'Luxury',NULL,925000,2025,40,'DETAILS','HAJJ',NULL,'[ "Duration: 40-43 Days", "Airlines: Saudi/Biman/Nas", "Flight Date: 5/7 Dhul Qadah - 17/19 Dhul Hijjah" ]'::jsonb,
    '[ "Hotel: Elaf Kinda/Makkah Tower/Safa Tower or similar", "Distance: 100 meter (Haram)", "Hotel Type: 5 Star", "Duration: 18/20 days (Before Hajj)", "Date: 5/7 - 25 Dhul Qadah", "Room: 4-5 Bed" ]'::jsonb,
    '[ "Apartment", "Distance : Nearest to Jamarat", "Duration : 10/12 Days", "Date: 5/7 Dhul Hijja & 10-17/19 Dhul Hijja", "Room : 4-5 Bed" ]'::jsonb,
    '[ "Hotel: Abraj Tabah/Grand Plaza/Safwat or similar", "Distance: 250 meter (Nabawi)", "Hotel Location: Inside Markazia Area", "Duration: 9 days (Befre Hajj)", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 4-5 Bed" ]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    now(), now(),NULL,NULL,true),
    (5,'Luxury',NULL,905000,2025,30,'DETAILS','HAJJ',NULL,'[ "Duration: 28-32 Days", "Airlines: Saudi/Biman/Nas", "Flight Date: 15/18 Dhul Qadah - 25 Dhul Hijjah" ]'::jsonb,
    '[ "Hotel: Elaf Kinda/Makkah Tower/Safa Tower or similar", "Distance: 100 meter (Haram)", "Hotel Type: 5 Star", "Duration: 10/7 days (Before Hajj)", "Date: 15/18 - 25 Dhul Qadah", "Room: 4-5 Bed" ]'::jsonb,
    '[ "Apartment", "Distance : Nearest to Jamarat", "Duration : 10/12 Days", "Date: 5/7 Dhul Hijja & 10-17/19 Dhul Hijja", "Room : 4-5 Bed" ]'::jsonb,
    '[ "Hotel: Abraj Tabah/Grand Plaza/Safwat or similar", "Distance: 250 meter (Nabawi)", "Hotel Location: Inside Markazia Area", "Duration: 8/9 days (Befre Hajj)", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 4-5 Bed" ]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    now(), now(),NULL,NULL,true),
    (6,'Exclusive',NULL,815000,2025,20,'DETAILS','HAJJ',NULL,'[ "Duration: 20-24 Days", "Airlines: Saudi/Biman/Nas" ]'::jsonb,
    '[]'::jsonb,
    '[ "Apartment", "Distance : Nearest to Jamarat", "Duration : 10/12 Days", "Date: 5/7 Dhul Hijja & 10-17/19 Dhul Hijja", "Room : 4-5 Bed" ]'::jsonb,
    '[ "Hotel: Abraj Tabah/Grand Plaza/Safwat or similar", "Distance: 250 meter (Nabawi)", "Hotel Location: Inside Markazia Area", "Duration: 8/9 days (Befre Hajj)", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 4-5 Bed" ]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    now(), now(),NULL,NULL,true),
    (7,'Standard',NULL,755000,2025,40,'DETAILS','HAJJ',NULL,'[ "Duration: 40-43 Days", "Airlines: Saudi/Biman/Nas", "Flight Date: 5/7 Dhul Qadah - 17/19 Dhul Hijjah" ]'::jsonb,
    '[ "Hotel: Emaar Andalusia/Emaar Dahabi or similar", "Distance: 500-850 meter (Haram)", "Hotel Type: 1/2 Star", "Duration: 18/20 days (Before Hajj)", "Date: 5/7 - 25 Dhul Qadah", "Room: 5-6 Bed" ]'::jsonb,
    '[ "Apartment", "Distance : Nearest to Jamarat", "Duration : 10/12 Days", "Date: 5/7 Dhul Hijja & 10-17/19 Dhul Hijja", "Room : 5-6 Bed" ]'::jsonb,
    '[ "Hotel: Arjwan Sada/Karam Cylinder/Karam Golden or similar", "Distance: 350-500 meter (Nabawi)", "Hotel Location: Inside Markazia Area", "Duration: 9 days (Befre Hajj)", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 5-6 Bed" ]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    now(), now(),NULL,NULL,true),
    (8,'Standard',NULL,745000,2025,30,'DETAILS','HAJJ',NULL,'[ "Duration: 28-32 Days", "Airlines: Saudi/Biman/Nas", "Flight Date: 15/18 Dhul Qadah - 25 Dhul Hijjah" ]'::jsonb,
    '[ "Hotel: Emaar Andalusia/Emaar Dahabi or similar", "Distance: 500-850 meter (Haram)", "Hotel Type: 1/2 Star", "Duration: 10/7 days (Before Hajj)", "Date: 15/18 - 25 Dhul Qadah", "Room: 5-6 Bed" ]'::jsonb,
    '[ "Apartment", "Distance : Nearest to Jamarat", "Duration : 10/12 Days", "Date: 5/7 Dhul Hijja & 10-17/19 Dhul Hijja", "Room : 5-6 Bed" ]'::jsonb,
    '[ "Hotel: Arjwan Sada/Karam Cylinder/Karam Golden or similar", "Distance: 350-500 meter (Nabawi)", "Hotel Location: Inside Markazia Area", "Duration: 8/9 days (Befre Hajj)", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 5-6 Bed" ]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    now(), now(),NULL,NULL,true),
    (9,'Standard',NULL,715000,2025,20,'DETAILS','HAJJ',NULL,'[ "Duration: 20-24 Days", "Airlines: Saudi/Biman/Nas" ]'::jsonb,
    '[]'::jsonb,
    '[ "Apartment", "Distance : Nearest to Jamarat", "Duration : 10/12 Days", "Date: 5/7 Dhul Hijja & 10-17/19 Dhul Hijja", "Room : 5-6 Bed" ]'::jsonb,
    '[ "Hotel: Arjwan Sada/Karam Cylinder/Karam Golden or similar", "Distance: 350-500 meter (Nabawi)", "Hotel Type: Inside Markazia Area", "Duration: 8/9 days (Befre Hajj)", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 5-6 Bed" ]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    now(), now(),NULL,NULL,true),
    (10,'Economy',NULL,580000,2025,40,'DETAILS','HAJJ',NULL,'[ "Duration: 40-43 Days", "Airlines: Saudi/Biman/Nas", "Flight Date: 5/7 Dhul Qadah - 17/19 Dhul Hijjah" ]'::jsonb,
    '[ "Hotel: Economy Hotel or Apartment", "Distance: 1-1.3 km (Haram)", "Duration: 18/20 days (Before Hajj)", "Date: 5/7 - 25 Dhul Qadah", "Room: 5-6 Bed" ]'::jsonb,
    '[ "Normal Apartment", "Distance : Nearest to Jamarat", "Duration : 10/12 Days", "Date: 5/7 Dhul Hijja & 10-17/19 Dhul Hijja", "Room : 5-6 Bed" ]'::jsonb,
    '[ "Hotel: Economy Hotel or Apartment", "Distance: 1-1.3 km (Nabawi)", "Hotel Location: Outside Markazia Area", "Duration: 9 days (Befre Hajj)", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 5-6 Bed" ]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    now(), now(),NULL,NULL,true),
    (11,'Economy',NULL,575000,2025,30,'DETAILS','HAJJ',NULL,'[ "Duration: 28-32 Days", "Airlines: Saudi/Biman/Nas", "Flight Date: 15/18 Dhul Qadah - 25 Dhul Hijjah" ]'::jsonb,
    '[ "Hotel: Economy Hotel or Apartment", "Distance: 1-1.3 km (Haram)", "Duration: 10/7 days (Before Hajj)", "Date: 15/18 - 25 Dhul Qadah", "Room: 5-6 Bed" ]'::jsonb,
    '[ "Normal Apartment", "Distance : Nearest to Jamarat", "Duration : 10/12 Days", "Date: 5/7 Dhul Hijja & 10-17/19 Dhul Hijja", "Room : 5-6 Bed" ]'::jsonb,
    '[ "Hotel: Economy Hotel or Apartment", "Distance: 1-1.3 km (Nabawi)", "Hotel Location: Outside Markazia Area", "Duration: 8/9 days (Befre Hajj)", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 5-6 Bed" ]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    now(), now(),NULL,NULL,true),
    (12,'Economy',NULL,550000,2025,20,'DETAILS','HAJJ',NULL,'[ "Duration: 20-24 Days", "Airlines: Saudi/Biman/Nas" ]'::jsonb,
    '[]'::jsonb,
    '[ "Normal Apartment", "Distance : Nearest to Jamarat", "Duration : 10/12 Days", "Date: 5/7 Dhul Hijja & 10-17/19 Dhul Hijja", "Room : 5-6 Bed" ]'::jsonb,
    '[ "Hotel: Economy Hotel or Apartment", "Distance: 1-1.3 km (Nabawi)", "Hotel Location: Outside Markazia Area", "Duration: 8/9 days (Befre Hajj)", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 5-6 Bed" ]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    now(), now(),NULL,NULL,true)
    """)


def downgrade() -> None:
    op.execute("DELETE FROM core.packages")
