import fastapi
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.core.utils.authorize_api import check_agency_or_staff_user
from app.service import flight_purchase_service
from data.db.db_config import get_async_db
from infrastructure.schema.flight_purchase_schema import (
    FlightPurchaseCreateSchema,
    FlightPurchaseUpdateSchema,
    FlightPurchaseResponseSchema,
    FlightPurchaseListResponseSchema,
    FlightPurchaseReconciliationResponseSchema,
)

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private", tags=["Flight Purchase"])


@private_router.post("/flight-purchase", response_model=FlightPurchaseResponseSchema)
async def create_flight_purchase(
        request: FlightPurchaseCreateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    username = current_user["username"]
    return await flight_purchase_service.create_flight_purchase(db, request, agency_name, username)


@private_router.get("/flight-purchase", response_model=FlightPurchaseListResponseSchema)
async def get_flight_purchases(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await flight_purchase_service.get_flight_purchases(db, agency_name)


@private_router.get("/flight-purchase/reconciliation", response_model=FlightPurchaseReconciliationResponseSchema)
async def get_flight_purchase_reconciliation(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    """Purchased vs. demanded seats per flight window (see GET /flight-demand)."""
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await flight_purchase_service.get_flight_purchase_reconciliation(db, agency_name)


@private_router.get("/flight-purchase/{purchase_id}", response_model=FlightPurchaseResponseSchema)
async def get_flight_purchase_by_id(
        purchase_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await flight_purchase_service.get_flight_purchase_by_id(db, purchase_id, agency_name)


@private_router.put("/flight-purchase", response_model=FlightPurchaseResponseSchema)
async def update_flight_purchase(
        request: FlightPurchaseUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    username = current_user["username"]
    return await flight_purchase_service.update_flight_purchase(db, request, agency_name, username)


@private_router.delete("/flight-purchase/{purchase_id}", response_model=FlightPurchaseListResponseSchema)
async def delete_flight_purchase(
        purchase_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await flight_purchase_service.delete_flight_purchase(db, purchase_id, agency_name)
