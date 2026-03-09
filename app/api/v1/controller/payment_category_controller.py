import fastapi
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.core.utils.authorize_api import check_agency_or_staff_user
from app.service import payment_category_service
from data.db.db_config import get_async_db
from infrastructure.schema.payment_category_schema import PaymentCategoryBase, PaymentCategoryUpdateSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")


@private_router.post("/payment-category", tags=["payment"])
async def create_payment_category(
        request: PaymentCategoryBase,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    username = current_user['username']
    return await payment_category_service.create_payment_category(db, request, agency_name, username)


@private_router.get("/payment-category", tags=["payment"])
async def list_payment_categories(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await payment_category_service.get_payment_category(db, agency_name)


@private_router.put("/payment-category", tags=["payment"])
async def update_payment_category(
        update_request: PaymentCategoryUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    username = current_user['username']
    return await payment_category_service.update_payment_category(db=db, update_request=update_request,
                                                                  agency_name=agency_name, username=username)


@private_router.get("/payment-category/{payment_category_id}", tags=["payment"])
async def get_payment_category_by_id(
        payment_category_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await payment_category_service.get_payment_category_by_id(db=db, payment_category_id=payment_category_id,
                                                                     agency_name=agency_name)


@private_router.delete("/payment-category/{payment_category_id}", tags=["payment"])
async def delete_payment_category(
        payment_category_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await payment_category_service.delete_payment_category(db=db, payment_category_id=payment_category_id,
                                                                  agency_name=agency_name)
