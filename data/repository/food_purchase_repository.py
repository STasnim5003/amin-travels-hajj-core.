from fastapi import HTTPException
from sqlalchemy import insert, select, delete, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from data.model.food_purchase_model import FoodPurchaseModel


async def create_food_purchase(db: AsyncSession, request_dict: dict):
    try:
        stmt = insert(FoodPurchaseModel).values(**request_dict).returning(FoodPurchaseModel)
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def get_food_purchases(db: AsyncSession, agency_name: str):
    try:
        result = await db.execute(
            select(FoodPurchaseModel)
            .where(FoodPurchaseModel.agency_name == agency_name)
            .order_by(FoodPurchaseModel.id.desc())
        )
        return result.scalars().all()
    except Exception as e:
        raise e


async def get_food_purchase_by_id(db: AsyncSession, purchase_id: int, agency_name: str):
    try:
        result = await db.execute(
            select(FoodPurchaseModel).where(FoodPurchaseModel.id == purchase_id)
        )
        purchase = result.scalar_one_or_none()
        if purchase is None or purchase.agency_name != agency_name:
            raise HTTPException(status_code=400, detail="Food purchase not found")
        return purchase
    except HTTPException:
        raise
    except Exception as e:
        raise e


async def update_food_purchase(db: AsyncSession, update_dict: dict, agency_name: str, username: str):
    try:
        purchase_id = update_dict.pop("id")
        purchase = await get_food_purchase_by_id(db, purchase_id, agency_name)

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


async def delete_food_purchase(db: AsyncSession, purchase_id: int, agency_name: str):
    try:
        purchase = await get_food_purchase_by_id(db, purchase_id, agency_name)

        await db.execute(delete(FoodPurchaseModel).where(FoodPurchaseModel.id == purchase.id))
        await db.commit()

        return await get_food_purchases(db, agency_name)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise e


async def get_food_purchase_reconciliation(db: AsyncSession, agency_name: str):
    try:
        query = text("""
            WITH demand AS (
                SELECT
                    f.name AS food_name,
                    COUNT(p.food_menu_id) AS number_of_hajji
                FROM core.pilgrim_data pd
                JOIN core.packages p
                  ON pd.package_name = p.name
                 AND pd.package_duration = p.duration
                JOIN core.food_menu f
                  ON p.food_menu_id = f.id
                WHERE pd.group_name = :agency_name
                  AND pd.registration_status = 'REGISTERED'
                GROUP BY f.name
            ),
            purchased AS (
                SELECT
                    food_name,
                    COALESCE(SUM(meals_purchased), 0) AS total_meals_purchased
                FROM core.food_purchase
                WHERE agency_name = :agency_name
                GROUP BY food_name
            )
            SELECT
                d.food_name,
                d.number_of_hajji,
                COALESCE(pu.total_meals_purchased, 0) AS total_meals_purchased,
                GREATEST(0, d.number_of_hajji - COALESCE(pu.total_meals_purchased, 0)) AS remaining_meals
            FROM demand d
            LEFT JOIN purchased pu
              ON d.food_name = pu.food_name
            ORDER BY d.food_name
        """)

        result = await db.execute(query, {"agency_name": agency_name})
        return result.mappings().all()
    except Exception as e:
        raise e
