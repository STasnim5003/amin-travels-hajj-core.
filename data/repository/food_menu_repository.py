from fastapi import HTTPException
from sqlalchemy import select, update, delete
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

async def get_food_menu_by_id(db: AsyncSession, food_menu_id:int, agency_name : str):
    result = await db.execute(select(FoodMenuModel).where(FoodMenuModel.id == food_menu_id))
    existing_menu = result.scalar_one_or_none()
    if not existing_menu:
        raise HTTPException(status_code=400, detail=f"Food menu not found")
    if existing_menu.agency_name != agency_name:
        raise HTTPException(status_code=400, detail=f"Agency name {agency_name} does not match")
    return existing_menu


async def update_food_menu(db:AsyncSession, update_request_dict:dict):
    try:
        stmt = (
            update(FoodMenuModel)
            .where(FoodMenuModel.id == update_request_dict.get('id'))
            .values(**update_request_dict)
            .returning(FoodMenuModel)
        )

        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def delete_food_menu(db:AsyncSession, food_menu_id:int):
    try:
        await db.execute(
            delete(FoodMenuModel).where(FoodMenuModel.id == food_menu_id)
        )
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))