from typing import Optional, List

import fastapi
from fastapi import Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user, get_current_admin_user
from app.service import payment_service
from data.db.db_config import get_async_db
from infrastructure.schema.payment_schema import PaymentResponseSchema, PaymentSchema, \
    PaginatedPaymentResponseForGroupLeader, PaginatedPaymentResponseForAgency, AgencyPaymentSchemaForGroupLeader

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")


@private_router.post("/group-leader/create-payable", response_model=PaymentResponseSchema, tags=["payment"])
async def create_payable_for_group_leader(
        payment_request: PaymentSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> PaymentResponseSchema:
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await payment_service.create_payable_for_group_leader(db, payment_request, agency_name)


# # @private_router.get("/group-leader/payable", tags=["payment"])
@private_router.post("/group-leader/create-payment", response_model=PaymentResponseSchema, tags=["payment"])
async def create_payment_of_group_leader(
        description: Optional[str] = Form(None),
        date: Optional[str] = Form(None),
        amount: int = Form(...),
        category: str = Form(...),
        group_leader: Optional[str] = Form(None),
        payable_id: int = Form(...),
        pilgrims_id: Optional[List[str]] = Form([]),
        receipt: Optional[List[UploadFile]] = File([]),
        db: AsyncSession = Depends(get_async_db),
        # current_user: dict = Depends(get_current_user)
) -> PaymentResponseSchema:
    # if current_user["role"] != "AGENCY":
    #     raise HTTPException(status_code=403, detail="Unauthorized")
    # agency_name = current_user['agency_name']
    agency_name = "MARVELLOUS"

    request_schema = AgencyPaymentSchemaForGroupLeader(
        description=description,
        date=date,
        amount=amount,
        category=category,
        group_leader=group_leader,
        payable_id=payable_id,
        pilgrims_id=pilgrims_id,
    )
    return await payment_service.create_group_leader_payment(db, request_schema, agency_name, receipt)


@private_router.get("/group-leader/payment-info", response_model=PaginatedPaymentResponseForGroupLeader,
                    tags=["payment"])
async def get_group_leader_payment_info(
        db: AsyncSession = Depends(get_async_db),
        category: str | None = Query(None, description="Filter by payment category"),
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=100),
        current_user: dict = Depends(get_current_admin_user)
):
    if current_user["role"] != "GROUP_LEADER":
        raise HTTPException(status_code=403, detail="Unauthorized")

    group_leader = current_user["code"]

    return await payment_service.get_group_leader_payments(
        db=db,
        group_leader=group_leader,
        category=category,
        page=page,
        size=size
    )


@private_router.get("/agency/payment-info", response_model=PaginatedPaymentResponseForAgency, tags=["payment"])
async def get_group_leader_payment_info(
        db: AsyncSession = Depends(get_async_db),
        category: str | None = Query(None, description="Filter by payment category"),
        group_leader: str | None = Query(None, description="Filter by group leader"),
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=100),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")

    agency_name = current_user["agency_name"]

    return await payment_service.get_agency_payments(
        db=db,
        agency_name=agency_name,
        group_leader=group_leader,
        category=category,
        page=page,
        size=size
    )
