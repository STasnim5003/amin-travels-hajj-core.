from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from data.repository import food_menu_repository
from infrastructure.schema.food_menu_schema import FoodMenuCreateSchema, FoodMenuUpdateSchema


async def create_food_menu(db: AsyncSession, food_menu: FoodMenuCreateSchema):
    try:
        return await food_menu_repository.create(db, food_menu)
    except Exception as e:
        raise

async def get_food_menus(db: AsyncSession, agency_name : str):
    return await food_menu_repository.get_all_food_menu(db, agency_name)

async def get_food_menu_by_id(db: AsyncSession, food_menu_id : int, agency_name : str):
    try:
        return await food_menu_repository.get_food_menu_by_id(db, food_menu_id, agency_name)
    except Exception as e:
        raise

async def update_food_menu(db:AsyncSession, update_request: FoodMenuUpdateSchema, agency_name:str):
    try:
        food_menu = await food_menu_repository.get_food_menu_by_id(db, update_request.id, agency_name)

        update_request_dict = update_request.model_dump(exclude_unset=True)
        update_request_dict['updated_by'] = agency_name

        updated_food_menu = await food_menu_repository.update_food_menu(db, update_request_dict)
        if not updated_food_menu:
            raise HTTPException(status_code=400, detail="Food Menu update failed")
        return updated_food_menu
    except Exception as e:
        raise e


async def delete_food_menu(db:AsyncSession, food_menu_id:int, agency_name:str):
    try:
        food_menu = await food_menu_repository.get_food_menu_by_id(db, food_menu_id, agency_name)
        if not food_menu:
            raise HTTPException(status_code=400, detail="Food Menu Not found")

        await food_menu_repository.delete_food_menu(db, food_menu_id)
        result = await food_menu_repository.get_all_food_menu(db, agency_name)
        return result
    except Exception as e:
        raise e

