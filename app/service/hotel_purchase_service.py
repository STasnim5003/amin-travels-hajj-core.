from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.file_downloadable_url import generate_downloadable_urls
from data.repository import hotel_purchase_repository
from infrastructure.schema.hotel_purchase_schema import (
    HotelPurchaseCreateSchema,
    HotelPurchaseUpdateSchema,
    HotelPurchaseResponseSchema,
    HotelPurchaseListResponseSchema,
    HotelPurchaseReconciliationItemSchema,
    HotelPurchaseReconciliationResponseSchema,
)


def _validate_amounts(rooms_purchased: dict, cost: float):
    if rooms_purchased is not None and any(count <= 0 for count in rooms_purchased.values()):
        raise HTTPException(status_code=400, detail="rooms_purchased counts must be greater than 0")
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


async def create_hotel_purchase(db: AsyncSession, request: HotelPurchaseCreateSchema, agency_name: str, username: str):
    try:
        _validate_amounts(request.rooms_purchased, request.cost)

        request_dict = request.model_dump(exclude_none=True)
        request_dict["agency_name"] = agency_name
        request_dict["created_by"] = username
        request_dict["updated_by"] = username
        if "booking_file" in request_dict:
            request_dict["booking_file"] = _normalize_booking_file(request_dict["booking_file"])

        result = await hotel_purchase_repository.create_hotel_purchase(db, request_dict)
        return HotelPurchaseResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def get_hotel_purchases(db: AsyncSession, agency_name: str):
    try:
        result = await hotel_purchase_repository.get_hotel_purchases(db, agency_name)
        purchases = []
        for item in result:
            if item.booking_file:
                item.booking_file = await generate_downloadable_urls(_normalize_booking_file(item.booking_file))
            purchases.append(HotelPurchaseResponseSchema.model_validate(item))

        return HotelPurchaseListResponseSchema(hotel_purchases=purchases)
    except Exception as e:
        raise e


async def get_hotel_purchase_by_id(db: AsyncSession, purchase_id: int, agency_name: str):
    try:
        result = await hotel_purchase_repository.get_hotel_purchase_by_id(db, purchase_id, agency_name)
        if result.booking_file:
            result.booking_file = await generate_downloadable_urls(_normalize_booking_file(result.booking_file))
        return HotelPurchaseResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def update_hotel_purchase(db: AsyncSession, request: HotelPurchaseUpdateSchema, agency_name: str, username: str):
    try:
        _validate_amounts(request.rooms_purchased, request.cost)

        update_dict = request.model_dump(exclude_none=True)
        if "booking_file" in update_dict:
            update_dict["booking_file"] = _normalize_booking_file(update_dict["booking_file"])
        result = await hotel_purchase_repository.update_hotel_purchase(db, update_dict, agency_name, username)
        return HotelPurchaseResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def delete_hotel_purchase(db: AsyncSession, purchase_id: int, agency_name: str):
    try:
        result = await hotel_purchase_repository.delete_hotel_purchase(db, purchase_id, agency_name)
        return HotelPurchaseListResponseSchema(
            hotel_purchases=[HotelPurchaseResponseSchema.model_validate(item) for item in result]
        )
    except Exception as e:
        raise e


async def get_hotel_purchase_reconciliation(db: AsyncSession, agency_name: str):
    try:
        rows = await hotel_purchase_repository.get_hotel_purchase_reconciliation(db, agency_name)

        windows = [
            HotelPurchaseReconciliationItemSchema(
                city=r["city"],
                category=r["category"],
                checkin=r["checkin"],
                checkout=r["checkout"],
                bed_type=r["bed_type"],
                number_of_hajji=r["number_of_hajji"],
                rooms_purchased=r["rooms_purchased"],
                remaining=r["remaining"],
            )
            for r in rows
        ]

        return HotelPurchaseReconciliationResponseSchema(windows=windows)
    except Exception as e:
        raise e
