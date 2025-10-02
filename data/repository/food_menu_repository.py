from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.food_menu_model import FoodMenuModel
from infrastructure.schema.food_menu_schema import FoodMenuCreateSchema


async def create(db: AsyncSession, food_menu: FoodMenuCreateSchema) -> FoodMenuModel:
    try:
        db_obj = FoodMenuModel(**food_menu.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def get_all_food_menu(db: AsyncSession, agency_name):
    result = await db.execute(select(FoodMenuModel).where(FoodMenuModel.agency_name == agency_name))
    return result.scalars().all()