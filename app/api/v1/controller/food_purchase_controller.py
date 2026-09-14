import fastapi
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.core.utils.authorize_api import check_agency_or_staff_user
from app.service import food_purchase_service
from data.db.db_config import get_async_db
from infrastructure.schema.food_purchase_schema import (
    FoodPurchaseCreateSchema,
    FoodPurchaseUpdateSchema,
    FoodPurchaseResponseSchema,
    FoodPurchaseListResponseSchema,
    FoodPurchaseReconciliationResponseSchema,
)

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private", tags=["Food Purchase"])


@private_router.post("/food-purchase", response_model=FoodPurchaseResponseSchema)
async def create_food_purchase(
        request: FoodPurchaseCreateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    username = current_user["username"]
    return await food_purchase_service.create_food_purchase(db, request, agency_name, username)


@private_router.get("/food-purchase", response_model=FoodPurchaseListResponseSchema)
async def get_food_purchases(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await food_purchase_service.get_food_purchases(db, agency_name)


@private_router.get("/food-purchase/reconciliation", response_model=FoodPurchaseReconciliationResponseSchema)
async def get_food_purchase_reconciliation(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    """Purchased vs. demanded meals per food menu (see GET /food-demand)."""
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await food_purchase_service.get_food_purchase_reconciliation(db, agency_name)


@private_router.get("/food-purchase/{purchase_id}", response_model=FoodPurchaseResponseSchema)
async def get_food_purchase_by_id(
        purchase_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await food_purchase_service.get_food_purchase_by_id(db, purchase_id, agency_name)


@private_router.put("/food-purchase", response_model=FoodPurchaseResponseSchema)
async def update_food_purchase(
        request: FoodPurchaseUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    username = current_user["username"]
    return await food_purchase_service.update_food_purchase(db, request, agency_name, username)


@private_router.delete("/food-purchase/{purchase_id}", response_model=FoodPurchaseListResponseSchema)
async def delete_food_purchase(
        purchase_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await food_purchase_service.delete_food_purchase(db, purchase_id, agency_name)
