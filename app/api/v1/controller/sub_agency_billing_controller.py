from typing import Optional

import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import sub_agency_billing_service
from data.db.db_config import get_async_db
from infrastructure.schema.payment_request_schema import PaymentRequestResponse, SubAgencyBillCreateSchema, \
    PaymentRequestListResponseSchema, SubAgencyBillUpdateSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private", tags=["sub agency billing"])


@private_router.post("/sub-agency-billing", response_model=PaymentRequestResponse)
async def create_sub_agency_bill(
        request: SubAgencyBillCreateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user : dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await sub_agency_billing_service.create_sub_agency_bill(db=db, request=request, agency_name=agency_name)

@private_router.get("/sub-agency-billing", response_model=PaymentRequestListResponseSchema)
async def create_sub_agency_bill(
        db: AsyncSession = Depends(get_async_db),
        current_user : dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await sub_agency_billing_service.get_sub_agency_bill(db=db, agency_name=agency_name)

@private_router.put("/sub-agency-billing", response_model=PaymentRequestResponse)
async def create_sub_agency_bill(
        request: SubAgencyBillUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user : dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await sub_agency_billing_service.update_sub_agency_bill(db=db, request=request,agency_name=agency_name)

@private_router.get("/sub-agency-billing/{bill_id}", response_model=PaymentRequestResponse)
async def get_bill_by_id(
        bill_id:int,
        db: AsyncSession = Depends(get_async_db),
        current_user : dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await sub_agency_billing_service.get_sub_agency_bill_by_id(db=db, agency_name=agency_name, bill_id:int)

@private_router.delete("/sub-agency-billing/{bill_id}")
async def delete_sub_agency_bill(
        bill_id : int,
        db: AsyncSession = Depends(get_async_db),
        current_user : dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await sub_agency_billing_service.delete_sub_agency_bill(db=db, bill_id = bill_id,agency_name=agency_name)
