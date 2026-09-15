import fastapi
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.core.utils.authorize_api import check_agency_or_staff_user
from app.service import route_purchase_service
from data.db.db_config import get_async_db
from infrastructure.schema.route_purchase_schema import (
    RoutePurchaseCreateSchema,
    RoutePurchaseUpdateSchema,
    RoutePurchaseResponseSchema,
    RoutePurchaseListResponseSchema,
    RoutePurchaseReconciliationResponseSchema,
)

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private", tags=["Route Purchase"])


@private_router.post("/route-purchase", response_model=RoutePurchaseResponseSchema)
async def create_route_purchase(
        request: RoutePurchaseCreateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    username = current_user["username"]
    return await route_purchase_service.create_route_purchase(db, request, agency_name, username)


@private_router.get("/route-purchase", response_model=RoutePurchaseListResponseSchema)
async def get_route_purchases(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await route_purchase_service.get_route_purchases(db, agency_name)


@private_router.get("/route-purchase/reconciliation", response_model=RoutePurchaseReconciliationResponseSchema)
async def get_route_purchase_reconciliation(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    """Purchased vs. demanded seats per route (see GET /route-demand)."""
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await route_purchase_service.get_route_purchase_reconciliation(db, agency_name)


@private_router.get("/route-purchase/{purchase_id}", response_model=RoutePurchaseResponseSchema)
async def get_route_purchase_by_id(
        purchase_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await route_purchase_service.get_route_purchase_by_id(db, purchase_id, agency_name)


@private_router.put("/route-purchase", response_model=RoutePurchaseResponseSchema)
async def update_route_purchase(
        request: RoutePurchaseUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    username = current_user["username"]
    return await route_purchase_service.update_route_purchase(db, request, agency_name, username)


@private_router.delete("/route-purchase/{purchase_id}", response_model=RoutePurchaseListResponseSchema)
async def delete_route_purchase(
        purchase_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await route_purchase_service.delete_route_purchase(db, purchase_id, agency_name)
