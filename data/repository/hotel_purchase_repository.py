from fastapi import HTTPException
from sqlalchemy import insert, select, delete, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from data.model.hotel_purchase_model import HotelPurchaseModel


async def create_hotel_purchase(db: AsyncSession, request_dict: dict):
    try:
        stmt = insert(HotelPurchaseModel).values(**request_dict).returning(HotelPurchaseModel)
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def get_hotel_purchases(db: AsyncSession, agency_name: str):
    try:
        result = await db.execute(
            select(HotelPurchaseModel)
            .where(HotelPurchaseModel.agency_name == agency_name)
            .order_by(HotelPurchaseModel.id.desc())
        )
        return result.scalars().all()
    except Exception as e:
        raise e


async def get_hotel_purchase_by_id(db: AsyncSession, purchase_id: int, agency_name: str):
    try:
        result = await db.execute(
            select(HotelPurchaseModel).where(HotelPurchaseModel.id == purchase_id)
        )
        purchase = result.scalar_one_or_none()
        if purchase is None or purchase.agency_name != agency_name:
            raise HTTPException(status_code=400, detail="Hotel purchase not found")
        return purchase
    except HTTPException:
        raise
    except Exception as e:
        raise e


async def update_hotel_purchase(db: AsyncSession, update_dict: dict, agency_name: str, username: str):
    try:
        purchase_id = update_dict.pop("id")
        purchase = await get_hotel_purchase_by_id(db, purchase_id, agency_name)

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


async def delete_hotel_purchase(db: AsyncSession, purchase_id: int, agency_name: str):
    try:
        purchase = await get_hotel_purchase_by_id(db, purchase_id, agency_name)

        await db.execute(delete(HotelPurchaseModel).where(HotelPurchaseModel.id == purchase.id))
        await db.commit()

        return await get_hotel_purchases(db, agency_name)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise e


async def get_hotel_purchase_reconciliation(db: AsyncSession, agency_name: str):
    try:
        query = text("""
            WITH base AS (
                SELECT 'makkah' AS city, pd.package_bed_types,
                       p.makkah::jsonb AS data
                FROM core.pilgrim_data pd
                JOIN core.packages p
                  ON pd.package_name = p.name
                 AND pd.package_duration = p.duration
                WHERE pd.group_name = :agency_name
                  AND pd.registration_status = 'REGISTERED'

                UNION ALL
                SELECT 'madinah', pd.package_bed_types, p.madinah::jsonb
                FROM core.pilgrim_data pd
                JOIN core.packages p
                  ON pd.package_name = p.name
                 AND pd.package_duration = p.duration
                WHERE pd.group_name = :agency_name
                  AND pd.registration_status = 'REGISTERED'

                UNION ALL
                SELECT 'azizia', pd.package_bed_types, p.azizia::jsonb
                FROM core.pilgrim_data pd
                JOIN core.packages p
                  ON pd.package_name = p.name
                 AND pd.package_duration = p.duration
                WHERE pd.group_name = :agency_name
                  AND pd.registration_status = 'REGISTERED'
            ),
            demand AS (
                SELECT city,
                       data ->> 'CheckIn' AS checkin,
                       data ->> 'CheckOut' AS checkout,
                       data ->> 'Category' AS category,
                       package_bed_types AS bed_type,
                       COUNT(*) AS number_of_hajji
                FROM base
                GROUP BY city, checkin, checkout, category, package_bed_types
            ),
            purchased AS (
                SELECT hp.city, hp.checkin, hp.checkout, hp.category,
                       kv.key AS bed_type,
                       SUM((kv.value)::int) AS rooms_purchased
                FROM core.hotel_purchase hp,
                     jsonb_each_text(hp.rooms_purchased) AS kv(key, value)
                WHERE hp.agency_name = :agency_name
                GROUP BY hp.city, hp.checkin, hp.checkout, hp.category, kv.key
            )
            SELECT
                d.city, d.checkin, d.checkout, d.category, d.bed_type,
                d.number_of_hajji,
                COALESCE(pu.rooms_purchased, 0) AS rooms_purchased,
                GREATEST(0, d.number_of_hajji - COALESCE(pu.rooms_purchased, 0)) AS remaining
            FROM demand d
            LEFT JOIN purchased pu
              ON d.city = pu.city
             AND d.checkin = pu.checkin
             AND d.checkout = pu.checkout
             AND d.category = pu.category
             AND d.bed_type = pu.bed_type
            ORDER BY d.city, d.checkin
        """)

        result = await db.execute(query, {"agency_name": agency_name})
        return result.mappings().all()
    except Exception as e:
        raise e
