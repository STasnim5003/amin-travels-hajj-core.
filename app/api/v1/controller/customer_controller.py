from typing import Optional

import fastapi
from fastapi import Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import customer_service, pilgrim_service
from data.db.db_config import get_async_db
from infrastructure.schema.customer_schema import CustomerCreateSchema, CustomerAppliedForRegistrationSchema
from infrastructure.schema.pilgrim_data_schema import PilgrimDataResponseSchema, PaginatedPilgrimDataListResponseSchema, \
    PilgrimRegistrationRequestSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")


@private_router.post("/customer", response_model=PilgrimDataResponseSchema, tags=["Customer"])
async def create_customer(
        customer: CustomerCreateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> PilgrimDataResponseSchema:
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    group_name = current_user["agency_name"]
    return await customer_service.create_customer(db, customer, group_name)


@private_router.put("/customer/applied-for-registration", response_model=PaginatedPilgrimDataListResponseSchema,
                    tags=["Customer"])
async def applied_for_registration(
        tracking_ids: CustomerAppliedForRegistrationSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> PaginatedPilgrimDataListResponseSchema:
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    group_name = current_user["agency_name"]
    response = await customer_service.customer_applied_for_registered(db, tracking_ids, group_name)
    return PaginatedPilgrimDataListResponseSchema(
        data=response,
        total=len(response),
        size=len(response),
        page=1
    )


@private_router.put("/customer/registration", tags=["Customer"])
async def customer_registration(
        vaccination_center: str = Form(...),
        package_id: int = Form(...),
        comment_on_package: Optional[str] = Form(None),
        passport_copy: UploadFile = File(...),
        tracking_id: str = Form(...),
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    try:
        return  await pilgrim_service.pilgrim_register(db, tracking_id, vaccination_center, passport_copy, package_id,
                                                      comment_on_package)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))