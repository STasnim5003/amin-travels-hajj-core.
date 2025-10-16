from http.client import HTTPException

import fastapi
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import payment_category_service
from data.db.db_config import get_async_db
from infrastructure.schema.payment_category_schema import PaymentCategoryBase


private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")

@private_router.post("/payment-category", tags=["payment"])
async def create_payment_category(
        request : PaymentCategoryBase,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await payment_category_service.create_payment_category(db, request, agency_name)

@private_router.get("/payment-category", tags=["payment"])
async def list_payment_categories(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await payment_category_service.get_payment_category(db, agency_name)
