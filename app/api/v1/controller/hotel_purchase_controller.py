import fastapi
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.core.utils.authorize_api import check_agency_or_staff_user
from app.service import hotel_purchase_service
from data.db.db_config import get_async_db
from infrastructure.schema.hotel_purchase_schema import (
    HotelPurchaseCreateSchema,
    HotelPurchaseUpdateSchema,
    HotelPurchaseResponseSchema,
    HotelPurchaseListResponseSchema,
    HotelPurchaseReconciliationResponseSchema,
)

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private", tags=["Hotel Purchase"])


@private_router.post("/hotel-purchase", response_model=HotelPurchaseResponseSchema)
async def create_hotel_purchase(
        request: HotelPurchaseCreateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    username = current_user["username"]
    return await hotel_purchase_service.create_hotel_purchase(db, request, agency_name, username)


@private_router.get("/hotel-purchase", response_model=HotelPurchaseListResponseSchema)
async def get_hotel_purchases(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await hotel_purchase_service.get_hotel_purchases(db, agency_name)


@private_router.get("/hotel-purchase/reconciliation", response_model=HotelPurchaseReconciliationResponseSchema)
async def get_hotel_purchase_reconciliation(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    """Purchased vs. demanded rooms per (city, checkin, checkout, category, bed_type)
    bucket (see GET /hotel-demand)."""
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await hotel_purchase_service.get_hotel_purchase_reconciliation(db, agency_name)


@private_router.get("/hotel-purchase/{purchase_id}", response_model=HotelPurchaseResponseSchema)
async def get_hotel_purchase_by_id(
        purchase_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await hotel_purchase_service.get_hotel_purchase_by_id(db, purchase_id, agency_name)


@private_router.put("/hotel-purchase", response_model=HotelPurchaseResponseSchema)
async def update_hotel_purchase(
        request: HotelPurchaseUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    username = current_user["username"]
    return await hotel_purchase_service.update_hotel_purchase(db, request, agency_name, username)


@private_router.delete("/hotel-purchase/{purchase_id}", response_model=HotelPurchaseListResponseSchema)
async def delete_hotel_purchase(
        purchase_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await hotel_purchase_service.delete_hotel_purchase(db, purchase_id, agency_name)
