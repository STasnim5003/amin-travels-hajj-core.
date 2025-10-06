from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import food_menu_repository
from infrastructure.schema.food_menu_schema import FoodMenuCreateSchema



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