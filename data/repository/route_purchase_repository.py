from fastapi import HTTPException
from sqlalchemy import insert, select, delete, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from data.model.route_purchase_model import RoutePurchaseModel


async def create_route_purchase(db: AsyncSession, request_dict: dict):
    try:
        stmt = insert(RoutePurchaseModel).values(**request_dict).returning(RoutePurchaseModel)
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def get_route_purchases(db: AsyncSession, agency_name: str):
    try:
        result = await db.execute(
            select(RoutePurchaseModel)
            .where(RoutePurchaseModel.agency_name == agency_name)
            .order_by(RoutePurchaseModel.id.desc())
        )
        return result.scalars().all()
    except Exception as e:
        raise e


async def get_route_purchase_by_id(db: AsyncSession, purchase_id: int, agency_name: str):
    try:
        result = await db.execute(
            select(RoutePurchaseModel).where(RoutePurchaseModel.id == purchase_id)
        )
        purchase = result.scalar_one_or_none()
        if purchase is None or purchase.agency_name != agency_name:
            raise HTTPException(status_code=400, detail="Route purchase not found")
        return purchase
    except HTTPException:
        raise
    except Exception as e:
        raise e


async def update_route_purchase(db: AsyncSession, update_dict: dict, agency_name: str, username: str):
    try:
        purchase_id = update_dict.pop("id")
        purchase = await get_route_purchase_by_id(db, purchase_id, agency_name)

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


async def delete_route_purchase(db: AsyncSession, purchase_id: int, agency_name: str):
    try:
        purchase = await get_route_purchase_by_id(db, purchase_id, agency_name)

        await db.execute(delete(RoutePurchaseModel).where(RoutePurchaseModel.id == purchase.id))
        await db.commit()

        return await get_route_purchases(db, agency_name)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise e


async def get_route_purchase_reconciliation(db: AsyncSession, agency_name: str):
    try:
        query = text("""
            WITH demand AS (
                SELECT
                    pd.package_duration,
                    r.description AS route_name,
                    COUNT(pd.id) AS number_of_hajji
                FROM core.pilgrim_data pd
                JOIN core.packages p
                  ON pd.package_name = p.name
                 AND pd.package_duration = p.duration
                JOIN core.route r
                  ON p.route_id = r.id
                WHERE pd.group_name = :agency_name
                  AND pd.registration_status = 'REGISTERED'
                GROUP BY pd.package_duration, r.description
            ),
            purchased AS (
                SELECT
                    package_duration,
                    route_name,
                    COALESCE(SUM(seats_purchased), 0) AS total_seats_purchased
                FROM core.route_purchase
                WHERE agency_name = :agency_name
                GROUP BY package_duration, route_name
            )
            SELECT
                d.package_duration,
                d.route_name,
                d.number_of_hajji,
                COALESCE(pu.total_seats_purchased, 0) AS total_seats_purchased,
                GREATEST(0, d.number_of_hajji - COALESCE(pu.total_seats_purchased, 0)) AS remaining_seats
            FROM demand d
            LEFT JOIN purchased pu
              ON d.package_duration = pu.package_duration
             AND d.route_name = pu.route_name
            ORDER BY d.package_duration DESC
        """)

        result = await db.execute(query, {"agency_name": agency_name})
        return result.mappings().all()
    except Exception as e:
        raise e
