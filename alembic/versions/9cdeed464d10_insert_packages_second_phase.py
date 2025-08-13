"""insert packages second phase

Revision ID: 9cdeed464d10
Revises: 81d66ba3c662
Create Date: 2025-08-13 04:52:40.966037

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9cdeed464d10'
down_revision: Union[str, Sequence[str], None] = '81d66ba3c662'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
            INSERT INTO core.packages (
        id, name, discount, price, hajj_year, duration, description_type, package_type, hajj_month,
        others_feature, makkah, azizia, madinah, includes, hotel_info, excludes,
        created_at, updated_at, created_by, updated_by, is_active
    ) VALUES (13,'Exclusive',NULL,NULL,2026,40,'DETAILS','HAJJ',NULL,'[ "Duration: 40-43 Days" ]'::jsonb,
        '[ "Hotel: Elaf Kinda/ Makkah Tower/ Safa Tower/ Clock Tower or similar", "Distance: 100 meter (Haram)", "Hotel Type: 4/5 Star", "Duration: 20 days", "Date: 5 Dhul Qadah - 25 Dhul Qadah", "Room: 4 Bed" ]'::jsonb,
        '[ "Quality Apartment near Jamarah Shuttle", "Distance : 1.5 km (Mina) & 5/6 km (Haram)", "Duration : 11/12 Days (Including Hajj Days)", "Date: 5 Dhul Hijja & 17/18 Dhul Hijja", "Room : 4 Bed" ]'::jsonb,
        '[ "Hotel: Anwar Al Medina Movenpick, Pulman Zamzam, Fontel Harathia, Golden Tulip AL Shakreen or similar", "Distance: 150 meter (Nabawi)", "Hotel Type: 4/5 Star", "Duration: 8/9 days", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 4 Bed" ]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        now(), now(),NULL,NULL,true),
        (14,'Exclusive',NULL,NULL,2026,30,'DETAILS','HAJJ',NULL,'[ "Duration: 28-32 Days" ]'::jsonb,
        '[ "Hotel: Elaf Kinda/ Makkah Tower/ Safa Tower/ Clock Tower or similar", "Distance: 100 meter (Haram)", "Hotel Type: 4/5 Star", "Duration: 7/10 days", "Date: 15/18 Dhul Qadah – 25 Dhul Qadah", "Room: 4 Bed" ]'::jsonb,
        '[ "Quality Apartment near Jamarah Shuttle Service", "Distance : 1.5 km (Mina) & 5/6 km (Haram)", "Duration : 11/12 Days (Including Hajj Days)", "Date: 5 Dhul Hijja & 17/18 Dhul Hijja", "Room : 4 Bed" ]'::jsonb,
        '[ "Hotel: Anwar Al Medina Movenpick, Pulman Zamzam, Fontel Harathia, Golden Tulip AL Shakreen or similar", "Distance: 150 meter (Nabawi)", "Hotel Type: 4/5 Star", "Duration: 8/9 days", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 4 Bed" ]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        now(), now(),NULL,NULL,true),
        (15,'Luxury',NULL,NULL,2026,40,'DETAILS','HAJJ',NULL,'[ "Duration: 40-43 Days" ]'::jsonb,
        '[ "Hotel: Elaf Kinda/ Makkah Tower/ Safa Tower/ Clock Tower or similar", "Distance: 100 meter (Haram)", "Hotel Type: 4/5 Star", "Duration: 20 days", "Date: 5 Dhul Qadah - 25 Dhul Qadah", "Room: 4-5 Bed" ]'::jsonb,
        '[ "Quality Apartment near Jamarah Shuttle", "Distance : 1.5 km (Mina) & 5/6 km (Haram)", "Duration : 11/12 Days (Including Hajj Days)", "Date: 5 Dhul Hijja & 17/18 Dhul Hijja", "Room : 4-5 Bed" ]'::jsonb,
        '[ "Hotel: Abraj Taba/ Mirage Al Salam/ Safwatul Medina/ Grand Plaza or similar", "Distance: 300 meter (Nabawi)", "Hotel Type: 2/3 Star", "Duration: 8/9 days", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 4-5 Bed" ]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        now(), now(),NULL,NULL,true),
        (16,'Luxury',NULL,NULL,2026,30,'DETAILS','HAJJ',NULL,'[ "Duration: 28-32 Days" ]'::jsonb,
        '[ "Hotel: Elaf Kinda/ Makkah Tower/ Safa Tower/ Clock Tower", "Distance: 100 meter (Haram)", "Hotel Type: 4/5 Star", "Duration: 7/10 days", "Date: 15/18 Dhul Qadah – 25 Dhul Qadah", "Room: 4-5 Bed" ]'::jsonb,
        '[ "Quality Apartment near Jamarah Shuttle Service", "Distance : 1.5 km (Mina) & 5/6 km (Haram)", "Duration : 11/12 Days (Including Hajj Days)", "Date: 5 Dhul Hijja & 17/18 Dhul Hijja", "Room : 4-5 Bed" ]'::jsonb,
        '[ "Hotel: Abraj Taba/ Mirage Al Salam/ Safwatul Medina/ Grand Plaza", "Distance: 300 meter (Nabawi)", "Hotel Type: 2/3 Star", "Duration: 8/9 days", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 4-5 Bed" ]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        now(), now(),NULL,NULL,true),
        (17,'Luxury',NULL,NULL,2026,20,'DETAILS','HAJJ',NULL,'[ "Duration: 20-24 Days" ]'::jsonb,
        '[]'::jsonb,
        '[ "Quality Apartment near Jamarah Shuttle Service", "Distance : 1.5 km (Mina) & 5/6 km (Haram)", "Duration : 11/12 Days (Including Hajj Days)", "Date: 5 Dhul Hijja & 17/18 Dhul Hijja", "Room : 4-5 Bed" ]'::jsonb,
        '[ "Hotel: Abraj Taba/ Mirage Al Salam/ Safwatul Medina/ Grand Plaza", "Distance: 300 meter (Nabawi)", "Hotel Type: 2/3 Star", "Duration: 8/9 days", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 4-5 Bed" ]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        now(), now(),NULL,NULL,true),
        (18,'Standard',NULL,NULL,2026,40,'DETAILS','HAJJ',NULL,'[ "Duration: 40-43 Days" ]'::jsonb,
        '[ "Hotel: Emar Andalus, Olyan Golden, Snood Ajiyad or similar", "Distance: 500-750 meter (Haram)", "Hotel Type: 2/3 Star", "Duration: 20 days", "Date: 5 Dhul Qadah - 25 Dhul Qadah", "Room: 5-6 Bed" ]'::jsonb,
        '[ "Quality Apartment near Jamarah Shuttle", "Distance : 1.5 km (Mina) & 5/6 km (Haram)", "Duration : 11/12 Days (Including Hajj Days)", "Date: 5 Dhul Hijja & 17/18 Dhul Hijja", "Room : 5-6 Bed" ]'::jsonb,
        '[ "Hotel: Medina Star, Arjuwan Sada or similar", "Distance: 350-400 meter (Nabawi)", "Hotel Type: 2/3 Star", "Duration: 8/9 days", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 5-6 Bed" ]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        now(), now(),NULL,NULL,true),
        (19,'Standard',NULL,NULL,2026,30,'DETAILS','HAJJ',NULL,'[ "Duration: 28-32 Days" ]'::jsonb,
        '[ "Hotel: Emar Andalus, Olyan Golden, Snood Ajiyad or similar", "Distance: 500-750 meter (Haram)", "Hotel Type: 2/3 Star", "Duration: 7/10 days", "Date: 15/18 Dhul Qadah – 25 Dhul Qadah", "Room: 4-5 Bed" ]'::jsonb,
        '[ "Quality Apartment near Jamarah Shuttle Service", "Distance : 1.5 km (Mina) & 5/6 km (Haram)", "Duration : 11/12 Days (Including Hajj Days)", "Date: 5 Dhul Hijja & 17/18 Dhul Hijja", "Room : 4-5 Bed" ]'::jsonb,
        '[ "Hotel: Medina Star, Arjuwan Sada or similar", "Distance: 350-400 meter (Nabawi)", "Hotel Type: 2/3 Star", "Duration: 8/9 days", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 4-5 Bed" ]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        now(), now(),NULL,NULL,true),
        (20,'Standard',NULL,NULL,2026,20,'DETAILS','HAJJ',NULL,'[ "Duration: 20-24 Days" ]'::jsonb,
        '[]'::jsonb,
        '[ "Quality Apartment near Jamarah Shuttle Service", "Distance : 1.5 km (Mina) & 5/6 km (Haram)", "Duration : 11/12 Days (Including Hajj Days)", "Date: 5 Dhul Hijja & 17/18 Dhul Hijja", "Room : 4-5 Bed" ]'::jsonb,
        '[ "Hotel: Medina Star, Arjuwan Sada or similar", "Distance: 350-400 meter (Nabawi)", "Hotel Type: 2/3 Star", "Duration: 8/9 days", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 4-5 Bed" ]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        now(), now(),NULL,NULL,true),
        (21,'Economy',NULL,NULL,2026,40,'DETAILS','HAJJ',NULL,'[ "Duration: 40-43 Days" ]'::jsonb,
        '[ "Hotel: Dar Al Khalil Rushd, Marsa Al Zaria or similar", "Distance: 900-1200 meter (Haram)", "Hotel Type: Economy", "Duration: 20 days", "Date: 5 Dhul Qadah - 25 Dhul Qadah", "Room: 5-7 Bed" ]'::jsonb,
        '[ "Normal Apartment near Jamarah", "Distance : 1.5 km (Mina) & 5/6 km (Haram)", "Duration : 11/12 Days (Including Hajj Days)", "Date: 5 Dhul Hijja & 17/18 Dhul Hijja", "Room : 5-7 Bed" ]'::jsonb,
        '[ "Hotel: Outside Markazia(Like Diar Al Aws)", "Distance: 550-850 meter (Nabawi)", "Hotel Type: Economy", "Duration: 8/9 days", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 5-7 Bed" ]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        now(), now(),NULL,NULL,true),
        (22,'Economy',NULL,NULL,2026,30,'DETAILS','HAJJ',NULL,'[ "Duration: 28-32 Days" ]'::jsonb,
        '[ "Hotel: Dar Al Khalil Rushd, Marsa Al Zaria or similar", "Distance: 900-1200 meter (Haram)", "Hotel Type: Economy", "Duration: 7/10 days", "Date: 15/18 Dhul Qadah – 25 Dhul Qadah", "Room: 5-7 Bed" ]'::jsonb,
        '[ "Normal Apartment near Jamarah", "Distance : 1.5 km (Mina) & 5/6 km (Haram)", "Duration : 11/12 Days (Including Hajj Days)", "Date: 5 Dhul Hijja & 17/18 Dhul Hijja", "Room : 5-7 Bed" ]'::jsonb,
        '[ "Hotel: Outside Markazia(Like Diar Al Aws)", "Distance: 550-850 meter (Nabawi)", "Hotel Type: Economy", "Duration: 8/9 days", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 5-7 Bed" ]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        now(), now(),NULL,NULL,true),
        (23,'Economy',NULL,NULL,2026,20,'DETAILS','HAJJ',NULL,'[ "Duration: 20-24 Days" ]'::jsonb,
        '[]'::jsonb,
        '[ "Normal Apartment near Jamarah", "Distance : 1.5 km (Mina) & 5/6 km (Haram)", "Duration : 11/12 Days (Including Hajj Days)", "Date: 5 Dhul Hijja & 17/18 Dhul Hijja", "Room : 4-5 Bed" ]'::jsonb,
        '[ "Hotel: Outside Markazia(Like Diar Al Aws)", "Distance: 550-850 meter (Nabawi)", "Hotel Type: Economy", "Duration: 8/9 days", "Date: 25 Dhul Qadah - 5 Dhul Hijja", "Room : 4-5 Bed" ]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        now(), now(),NULL,NULL,true),
        (24,'Exclusive',NULL,NULL,2026,40,'SHORT','HAJJ',NULL,'[]'::jsonb,
        '[ "Hotel: 4/5 Star", "Distance: 100 meter (Haram)", "Room: 4 Bed" ]'::jsonb,
        '[ "Apartment", "Distance : 1.5 km (Mina) & 5/6 km (Haram)",  "Room: 4 Bed" ]'::jsonb,
        '[ "Hotel: 4/5 Star", "Distance: 150 meter (Nabawi)", "Room: 4 Bed" ]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        now(), now(),NULL,NULL,true)
        """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM core.packages")
