from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

async def get_flight_demand(db:AsyncSession, agency_name: str):
    try:
        query = text("""
            SELECT
                (p.flight_date ->> 'english_calendar_start') AS english_start,
                (p.flight_date ->> 'arabic_calendar_start') AS arabic_start,
                (p.flight_date ->> 'arabic_calendar_end') AS arabic_end,
                (p.flight_date ->> 'english_calendar_end') AS english_end,
                COUNT(pd.id) AS pilgrim_count
            FROM core.pilgrim_data pd
            JOIN core.packages p
              ON pd.package_name = p.name
             AND pd.package_duration = p.duration
            WHERE pd.group_name = :agency_name
            AND pd.registration_status = 'REGISTERED'
            GROUP BY english_start, arabic_start, arabic_end, english_end
            ORDER BY english_start
        """)

        result = await db.execute(query, {"agency_name": agency_name})
        rows = result.mappings().all()

        return rows

    except Exception as e:
        raise e

async def get_route_demand(db:AsyncSession, agency_name:str):
    try:
        query = text("""
                SELECT
                    pd.package_name,
                    pd.package_duration,
                    r.description,
                    COUNT(pd.id) AS pilgrim_count
                FROM core.pilgrim_data pd
                JOIN core.packages p
                  ON pd.package_name = p.name
                 AND pd.package_duration = p.duration
                JOIN core.route r
                  ON p.route_id = r.id
                WHERE pd.group_name = :agency_name
                  AND pd.registration_status = 'REGISTERED'
                GROUP BY
                    pd.package_name,
                    pd.package_duration,
                    r.description
                ORDER BY
                    pd.package_name,
                    pd.package_duration
            """)

        result = await db.execute(query, {"agency_name": agency_name})
        rows = result.mappings().all()

        return rows

    except Exception as e:
        raise e

async def get_food_demand(db:AsyncSession, agency_name:str):
    try:
        query = text("""
                SELECT
                    COUNT(p.food_menu_id) AS menu_count,
                    f.name AS food_menu_name,
                    f.items AS food_items
                FROM core.pilgrim_data pd
                JOIN core.packages p
                  ON pd.package_name = p.name
                 AND pd.package_duration = p.duration
                JOIN core.food_menu f
                  ON p.food_menu_id = f.id
                WHERE pd.group_name = :agency_name
                  AND pd.registration_status = 'REGISTERED'
                GROUP BY f.name, f.items
                ORDER BY f.name
            """)

        result = await db.execute(query, {"agency_name": agency_name})
        rows = result.mappings().all()  # list[dict]

        return rows

    except Exception as e:
        raise e