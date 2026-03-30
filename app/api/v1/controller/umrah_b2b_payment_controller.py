import fastapi
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.core.utils.authorize_api import check_agency_or_staff_user
from data.db.db_config import get_async_db
from app.service import umrah_b2b_payment_service
from infrastructure.schema.umrah_b2b_payment_schema import (
    UmrahB2BPaymentCreate,
    UmrahB2BPaymentResponse,
    UmrahB2BPaymentListResponse,
    UmrahB2BPaymentUpdate
)

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private", tags=["Umrah B2B Payment"])

@private_router.post("/umrah/b2b-payment", response_model=UmrahB2BPaymentResponse)
async def create_payment(
        request: UmrahB2BPaymentCreate,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user),
):
    check_agency_or_staff_user(current_user)
    return await umrah_b2b_payment_service.create_umrah_b2b_payment(
        db, request,
        agency_name=current_user["agency_name"],
        username=current_user["username"]
    )


@private_router.get("/umrah/b2b-payment", response_model=UmrahB2BPaymentListResponse)
async def get_payments(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user),
):
    check_agency_or_staff_user(current_user)
    return await umrah_b2b_payment_service.get_umrah_b2b_payments(
        db, current_user["agency_name"]
    )


@private_router.put("/umrah/b2b-payment", response_model=UmrahB2BPaymentResponse)
async def update_payment(
        request: UmrahB2BPaymentUpdate,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user),
):
    check_agency_or_staff_user(current_user)
    return await umrah_b2b_payment_service.update_umrah_b2b_payment(
        db, request,
        agency_name=current_user["agency_name"],
        username=current_user["username"]
    )

@private_router.get("/umrah/b2b-payment/{payment_id}", response_model=UmrahB2BPaymentResponse)
async def get_payment_by_id(
        payment_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user),
):
    check_agency_or_staff_user(current_user)
    return await umrah_b2b_payment_service.get_umrah_b2b_payment_by_id(
        db, current_user["agency_name"], payment_id
    )

@private_router.delete("/umrah/b2b-payment/{payment_id}")
async def delete_payment(
        payment_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user),
):
    check_agency_or_staff_user(current_user)
    return await umrah_b2b_payment_service.delete_umrah_b2b_payment(
        db, current_user["agency_name"], payment_id, current_user['username']
    )