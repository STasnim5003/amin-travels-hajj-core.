from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.file_downloadable_url import generate_downloadable_urls
from data.repository import food_purchase_repository
from infrastructure.schema.food_purchase_schema import (
    FoodPurchaseCreateSchema,
    FoodPurchaseUpdateSchema,
    FoodPurchaseResponseSchema,
    FoodPurchaseListResponseSchema,
    FoodPurchaseReconciliationItemSchema,
    FoodPurchaseReconciliationResponseSchema,
)


def _validate_amounts(meals_purchased: int, cost: float):
    if meals_purchased is not None and meals_purchased <= 0:
        raise HTTPException(status_code=400, detail="meals_purchased must be greater than 0")
    if cost is not None and cost < 0:
        raise HTTPException(status_code=400, detail="cost cannot be negative")


def _normalize_booking_file(booking_file):
    """Coerce booking_file into the project's standard file-metadata shape:
    a list of dicts each containing 'file_url' (see file_repository.upload_file)."""
    if not booking_file:
        return booking_file
    if isinstance(booking_file, str):
        return [{"file_url": booking_file}]
    if isinstance(booking_file, dict):
        return [booking_file]
    return booking_file


async def create_food_purchase(db: AsyncSession, request: FoodPurchaseCreateSchema, agency_name: str, username: str):
    try:
        _validate_amounts(request.meals_purchased, request.cost)

        request_dict = request.model_dump(exclude_none=True)
        request_dict["agency_name"] = agency_name
        request_dict["created_by"] = username
        request_dict["updated_by"] = username
        if "booking_file" in request_dict:
            request_dict["booking_file"] = _normalize_booking_file(request_dict["booking_file"])

        result = await food_purchase_repository.create_food_purchase(db, request_dict)
        return FoodPurchaseResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def get_food_purchases(db: AsyncSession, agency_name: str):
    try:
        result = await food_purchase_repository.get_food_purchases(db, agency_name)
        purchases = []
        for item in result:
            if item.booking_file:
                item.booking_file = await generate_downloadable_urls(_normalize_booking_file(item.booking_file))
            purchases.append(FoodPurchaseResponseSchema.model_validate(item))

        return FoodPurchaseListResponseSchema(food_purchases=purchases)
    except Exception as e:
        raise e


async def get_food_purchase_by_id(db: AsyncSession, purchase_id: int, agency_name: str):
    try:
        result = await food_purchase_repository.get_food_purchase_by_id(db, purchase_id, agency_name)
        if result.booking_file:
            result.booking_file = await generate_downloadable_urls(_normalize_booking_file(result.booking_file))
        return FoodPurchaseResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def update_food_purchase(db: AsyncSession, request: FoodPurchaseUpdateSchema, agency_name: str, username: str):
    try:
        _validate_amounts(request.meals_purchased, request.cost)

        update_dict = request.model_dump(exclude_none=True)
        if "booking_file" in update_dict:
            update_dict["booking_file"] = _normalize_booking_file(update_dict["booking_file"])
        result = await food_purchase_repository.update_food_purchase(db, update_dict, agency_name, username)
        return FoodPurchaseResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def delete_food_purchase(db: AsyncSession, purchase_id: int, agency_name: str):
    try:
        result = await food_purchase_repository.delete_food_purchase(db, purchase_id, agency_name)
        return FoodPurchaseListResponseSchema(
            food_purchases=[FoodPurchaseResponseSchema.model_validate(item) for item in result]
        )
    except Exception as e:
        raise e


async def get_food_purchase_reconciliation(db: AsyncSession, agency_name: str):
    try:
        rows = await food_purchase_repository.get_food_purchase_reconciliation(db, agency_name)

        food_items = [
            FoodPurchaseReconciliationItemSchema(
                food_name=r["food_name"],
                number_of_hajji=r["number_of_hajji"],
                total_meals_purchased=r["total_meals_purchased"],
                remaining_meals=r["remaining_meals"],
            )
            for r in rows
        ]

        return FoodPurchaseReconciliationResponseSchema(food_items=food_items)
    except Exception as e:
        raise e
