from fastapi import HTTPException
from sqlalchemy import insert, select, delete, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from data.model.flight_purchase_model import FlightPurchaseModel


async def create_flight_purchase(db: AsyncSession, request_dict: dict):
    try:
        stmt = insert(FlightPurchaseModel).values(**request_dict).returning(FlightPurchaseModel)
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def get_flight_purchases(db: AsyncSession, agency_name: str):
    try:
        result = await db.execute(
            select(FlightPurchaseModel)
            .where(FlightPurchaseModel.agency_name == agency_name)
            .order_by(FlightPurchaseModel.id.desc())
        )
        return result.scalars().all()
    except Exception as e:
        raise e


async def get_flight_purchase_by_id(db: AsyncSession, purchase_id: int, agency_name: str):
    try:
        result = await db.execute(
            select(FlightPurchaseModel).where(FlightPurchaseModel.id == purchase_id)
        )
        purchase = result.scalar_one_or_none()
        if purchase is None or purchase.agency_name != agency_name:
            raise HTTPException(status_code=400, detail="Flight purchase not found")
        return purchase
    except HTTPException:
        raise
    except Exception as e:
        raise e


async def update_flight_purchase(db: AsyncSession, update_dict: dict, agency_name: str, username: str):
    try:
        purchase_id = update_dict.pop("id")
        purchase = await get_flight_purchase_by_id(db, purchase_id, agency_name)

        for key, value in update_dict.items():
            setattr(purchase, key, value)
        purchase.updated_by = username
        purchase.updated_at = get_current_time()

        await db.commit()
        await db.refresh(purchase)
        return purchase
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise e


async def delete_flight_purchase(db: AsyncSession, purchase_id: int, agency_name: str):
    try:
        purchase = await get_flight_purchase_by_id(db, purchase_id, agency_name)

        await db.execute(delete(FlightPurchaseModel).where(FlightPurchaseModel.id == purchase.id))
        await db.commit()

        return await get_flight_purchases(db, agency_name)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise e


async def get_flight_purchase_reconciliation(db: AsyncSession, agency_name: str):
    try:
        query = text("""
            WITH demand AS (
                SELECT
                    (p.flight_date ->> 'english_calendar_start') AS english_start,
                    (p.flight_date ->> 'arabic_calendar_start') AS arabic_start,
                    (p.flight_date ->> 'arabic_calendar_end') AS arabic_end,
                    (p.flight_date ->> 'english_calendar_end') AS english_end,
                    COUNT(pd.id) AS number_of_hajji
                FROM core.pilgrim_data pd
                JOIN core.packages p
                  ON pd.package_name = p.name
                 AND pd.package_duration = p.duration
                WHERE pd.group_name = :agency_name
                  AND pd.registration_status = 'REGISTERED'
                GROUP BY english_start, arabic_start, arabic_end, english_end
            ),
            purchased AS (
                SELECT
                    (flight_date_start ->> 'english_calendar') AS english_start,
                    (flight_date_end ->> 'english_calendar') AS english_end,
                    COALESCE(SUM(seats_purchased), 0) AS total_seats_purchased
                FROM core.flight_purchase
                WHERE agency_name = :agency_name
                GROUP BY english_start, english_end
            )
            SELECT
                d.english_start,
                d.arabic_start,
                d.arabic_end,
                d.english_end,
                d.number_of_hajji,
                COALESCE(pu.total_seats_purchased, 0) AS total_seats_purchased,
                GREATEST(0, d.number_of_hajji - COALESCE(pu.total_seats_purchased, 0)) AS remaining_seats
            FROM demand d
            LEFT JOIN purchased pu
              ON d.english_start = pu.english_start
             AND d.english_end = pu.english_end
            ORDER BY d.english_start
        """)

        result = await db.execute(query, {"agency_name": agency_name})
        return result.mappings().all()
    except Exception as e:
        raise e
