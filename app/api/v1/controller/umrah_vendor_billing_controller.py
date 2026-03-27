from typing import List

import fastapi
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.core.utils.authorize_api import check_agency_or_staff_user
from app.service import umrah_vendor_billing_service
from data.db.db_config import get_async_db
from infrastructure.schema.umrah_vendor_billing_schema import UmrahVendorBillingCreateSchema, \
    UmrahVendorBillingResponseSchema, UmrahVendorBillingDetailsResponseSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private", tags=["Umrah Billing"])


@private_router.post("/umrah/vendor-billing", response_model=UmrahVendorBillingResponseSchema)
async def create_umrah_vendor_billing(
        request: UmrahVendorBillingCreateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    username = current_user["username"]
    return await umrah_vendor_billing_service.create_umrah_vendor_billing(db=db, request=request,
                                                                          agency_name=agency_name, username=username)


@private_router.get("/umrah/vendor-billing", response_model=List[UmrahVendorBillingDetailsResponseSchema])
async def get_umrah_vendor_billing(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]

    return await umrah_vendor_billing_service.get_umrah_vendor_billing(db=db, agency_name=agency_name)

@private_router.get("/umrah/vendor-billing-summary/{vendor_name}", response_model=List[UmrahVendorBillingResponseSchema])
async def get_umrah_vendor_billing_summary(
        vendor_name: str,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await umrah_vendor_billing_service.get_vendor_billing_summary(db=db, agency_name=agency_name, vendor_name=vendor_name)