from typing import List

import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import food_menu_service
from data.db.db_config import get_async_db
from infrastructure.schema.food_menu_schema import FoodMenuResponseSchema, FoodMenuCreateSchema, FoodMenuBaseSchema, \
    FoodMenuUpdateSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")

@private_router.post("/food-menu", response_model=FoodMenuResponseSchema, tags=["Food Menu"])
async def create_food_menu(
        food_menu: FoodMenuBaseSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]

    food_menu_schema = FoodMenuCreateSchema(
        name=food_menu.name,
        agency_name=agency_name,
        items=food_menu.items,
        is_publish=food_menu.is_publish,
        area = food_menu.area,
        created_by=agency_name,
        updated_by=agency_name
    )

    return await food_menu_service.create_food_menu(db, food_menu_schema)


@private_router.get("/food-menu", tags=["Food Menu"])
async def get_food_menus(db: AsyncSession = Depends(get_async_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await food_menu_service.get_food_menus(db,agency_name)

@private_router.put("/food-menu", tags=["Food Menu"])
async def update_food_menu(
        update_request: FoodMenuUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await food_menu_service.update_food_menu(db=db, update_request=update_request, agency_name=agency_name)

@private_router.get("/food-menu/{food_menu_id}", tags=["Food Menu"])
async def get_food_menu_by_id(
        food_menu_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await food_menu_service.get_food_menu_by_id(db, food_menu_id, agency_name)

@private_router.delete("/food-menu/{food_menu_id}", tags=["Food Menu"])
async def delete_food_menu(
        food_menu_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await food_menu_service.delete_food_menu(db=db, food_menu_id=food_menu_id, agency_name=agency_name)