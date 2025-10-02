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