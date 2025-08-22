"""insert_october_umrah_packages

Revision ID: f6effa426859
Revises: 5c6278cf49a4
Create Date: 2025-08-22 16:35:04.759365

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6effa426859'
down_revision: Union[str, Sequence[str], None] = '5c6278cf49a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO core.packages (
            id, name, discount, price, hajj_year, duration, description_type, package_type, hajj_month,
            others_feature, makkah, azizia, madinah, includes, hotel_info, excludes,
            created_at, updated_at, created_by, updated_by, is_active
        ) VALUES (33,'Deluxe',NULL,180000,2025,14,'DETAILS','UMRAH','October','[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '["Umrah visa with insurance", "Dhaka- Madinah, Jeddah-Dhaka Economy Class Air Ticket by direct flight", "Makkah & Madinah Hotel Accomodation", "Riyadul Jannat Salat permit", "Full Ground Transport", "Makkah & Madinah Ziyarah", "Umrah Guide Service"]'::jsonb,
        '[{"Makkah": ["Duration 300-450 meter", "Hotel: AREEJ AL-FALAH", "Room Type 2-4 Shared"]}, {"Madinah": ["Duration : 300-450 meter", "Hotel: HAYA AL HUDA", "Room Type 2-4 Shared"]}]'::jsonb,
        '["All Category Food", "Any Type of Personal Expenses", "Zamzam Water", "Jeddah-Tayef-Badr & Any Tour is Not Included in this Package"]'::jsonb,
        now(), now(),NULL,NULL,true),
        (34,'Standard',NULL,170000,2025,14,'DETAILS','UMRAH','October','[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '["Umrah visa with insurance", "Dhaka- Madinah, Jeddah-Dhaka Economy Class Air Ticket by direct flight", "Makkah & Madinah Hotel Accomodation", "Riyadul Jannat Salat permit", "Full Ground Transport", "Makkah & Madinah Ziyarah", "Umrah Guide Service"]'::jsonb,
        '[{"Makkah": ["Duration 600-750 meter", "Hotel: Balora Al Taj Hotel", "Room Type 2-4 Shared"]}, {"Madinah": ["Duration : 300-450 meter", "Hotel: HAYA AL HUDA", "Room Type 2-4 Shared"]}]'::jsonb,
        '["All Category Food", "Any Type of Personal Expenses", "Zamzam Water", "Jeddah-Tayef-Badr & Any Tour is Not Included in this Package"]'::jsonb,
        now(), now(),NULL,NULL,true),
        (35,'Economy',NULL,150000,2025,14,'DETAILS','UMRAH','October','[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '[]'::jsonb,
        '["Umrah visa with insurance", "Dhaka- Madinah, Jeddah-Dhaka Economy Class Air Ticket by direct flight", "Makkah & Madinah Hotel Accomodation", "Riyadul Jannat Salat permit", "Full Ground Transport", "Makkah & Madinah Ziyarah", "Umrah Guide Service"]'::jsonb,
        '[{"Makkah": ["Duration 950-1100 meter", "Hotel: DAR AL WAFEDIN", "Room Type 2-4 Shared"]}, {"Madinah": ["Duration : 950-1100 meter", "Hotel: Marsa Al Khair", "Room Type 2-4 Shared"]}]'::jsonb,
        '["All Category Food", "Any Type of Personal Expenses", "Zamzam Water", "Jeddah-Tayef-Badr & Any Tour is Not Included in this Package"]'::jsonb,
        now(), now(),NULL,NULL,true)
        """)

    op.execute("""
            UPDATE core.packages
            SET duration = 14
            WHERE hajj_month = 'September'
              AND hajj_year = 2025
              AND package_type = 'UMRAH'
        """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
            DELETE FROM core.packages
            WHERE id IN (33, 34, 35)
        """)
