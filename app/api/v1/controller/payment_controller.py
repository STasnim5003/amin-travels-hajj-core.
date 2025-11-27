import json
from typing import Optional

import fastapi
from fastapi import Depends, HTTPException, Query, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.controller.pilgrim_controller import public_router
from app.core.middleware.middleware import get_current_user, get_current_admin_user, get_current_pilgrim
from app.service import payment_service, pilgrim_payment_service
from data.db.db_config import get_async_db
from infrastructure.schema.payment_schema import PaymentResponseSchema, PaginatedPaymentResponseForGroupLeader, \
    PaginatedPaymentResponseForAgency, GroupLeaderPayableBaseSchema, PilgrimPayableBaseSchema, \
    PilgrimPaymentBaseSchema, \
    GroupLeaderPaymentBaseSchema, PayableUpdateSchema, PaymentUpdateSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")


@private_router.post("/group-leader/create-payable", tags=["payment"])
async def create_payable_for_group_leader(
        request: GroupLeaderPayableBaseSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]

    return await payment_service.create_payable_for_group_leader(db, request, agency_name)


@private_router.post("/group-leader/create-payment", response_model=PaymentResponseSchema, tags=["payment"])
async def create_payment_of_group_leader(
        group_leader: str = Form(...),
        pilgrims_tracking_id: Optional[str] = Form(None),
        bank_info_id: Optional[int] = Form(None),
        way_of_payment: Optional[str] = Form(None),
        transfer_no: Optional[str] = Form(None),
        description: Optional[str] = Form(None),
        date: Optional[str] = Form(None),
        amount: int = Form(...),
        payment_category: Optional[str] = Form(None),
        voucher_no: Optional[str] = Form(None),
        cheque_no: Optional[str] = Form(None),
        cheque_bank: Optional[str] = Form(None),
        receipt: Optional[UploadFile] = File(None),
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> PaymentResponseSchema:
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user['agency_name']

    tracking_ids = []
    if pilgrims_tracking_id:
        try:
            tracking_ids = json.loads(pilgrims_tracking_id)
        except json.JSONDecodeError:
            tracking_ids = [pilgrims_tracking_id]

    request_schema = GroupLeaderPaymentBaseSchema(
        group_leader=group_leader,
        pilgrims_tracking_id=tracking_ids,
        bank_info_id=bank_info_id,
        way_of_payment=way_of_payment,
        transfer_no=transfer_no,
        description=description,
        date=date,
        amount=amount,
        category="Payment",
        payment_category=payment_category,
        voucher_no=voucher_no,
        cheque_no=cheque_no,
        cheque_bank=cheque_bank
    )
    return await payment_service.create_group_leader_payment(db, request_schema, agency_name, receipt)


@private_router.get("/group-leader/payment-info", response_model=PaginatedPaymentResponseForGroupLeader,
                    tags=["payment"])
async def get_group_leader_payment_info(
        db: AsyncSession = Depends(get_async_db),
        category: str | None = Query(None, description="Filter by payment category"),
        page: int = Query(1, ge=1),
        size: int = Query(100, ge=1),
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
async def get_agency_payment_info(
        user_type: str = Query("GROUP_LEADER", description="Filter by payment type"),
        db: AsyncSession = Depends(get_async_db),
        category: str | None = Query(None, description="Filter by payment category"),
        group_leader: str | None = Query(None, description="Filter by group leader"),
        tracking_id: str | None = Query(None),
        page: int = Query(1, ge=1),
        size: int = Query(100, ge=1),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")

    agency_name = current_user["agency_name"]

    return await payment_service.get_agency_payments(
        user_type, db, agency_name, group_leader, tracking_id, page, size
    )


@private_router.put("/update-payable", response_model=PaymentResponseSchema, tags=["payment"])
async def update_payable(
        payable_request: PayableUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> PaymentResponseSchema:
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]

    return await payment_service.update_payable(db, payable_request, agency_name)

@private_router.put("/update-payment", tags=["payment"])
async def update_payment(
        db: AsyncSession = Depends(get_async_db),
        payment_id: int = Form(...),
        group_leader: Optional[str] = Form(None),
        tracking_id : Optional[str] = Form(None),
        amount: Optional[int] = Form(None),
        description: Optional[str] = Form(None),
        date: Optional[str] = Form(None),
        payment_category: Optional[str] = Form(None),
        bank_info_id: Optional[int] = Form(None),
        way_of_payment: Optional[str] = Form(None),
        transfer_no: Optional[str] = Form(None),
        voucher_no: Optional[str] = Form(None),
        cheque_no: Optional[str] = Form(None),
        cheque_bank: Optional[str] = Form(None),
        receipt: Optional[UploadFile] = File(None),
        pilgrims_tracking_id: Optional[str] = Form(None),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    payment_update_schema = PaymentUpdateSchema(
        payment_id = payment_id,
        tracking_id=tracking_id,
        group_leader=group_leader,
        amount=amount,
        description=description,
        date=date,
        payment_category=payment_category,
        bank_info_id=bank_info_id,
        way_of_payment=way_of_payment,
        transfer_no=transfer_no,
        voucher_no=voucher_no,
        cheque_no=cheque_no,
        cheque_bank=cheque_bank,
        pilgrims_tracking_id=pilgrims_tracking_id
    )

    return await pilgrim_payment_service.update_payment(db=db, payment_update_schema=payment_update_schema, agency_name=agency_name, receipt=receipt)



@private_router.post("/pilgrim/create-payable", response_model=PaymentResponseSchema, tags=["payment"])
async def create_payable_for_pilgrim(
        request: PilgrimPayableBaseSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> PaymentResponseSchema:
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]

    result = await pilgrim_payment_service.create_payable_for_pilgrim(db, request, agency_name)
    return PaymentResponseSchema.model_validate(result)


@private_router.post("/pilgrim/create-payment", response_model=PaymentResponseSchema, tags=["payment"])
async def create_payment_for_pilgrim(
        amount: int = Form(...),
        tracking_id: str = Form(...),
        description: Optional[str] = Form(None),
        date: Optional[str] = Form(None),
        payment_category: Optional[str] = Form(None),
        bank_info_id: Optional[int] = Form(None),
        way_of_payment: Optional[str] = Form(None),
        transfer_no: Optional[str] = Form(None),
        voucher_no: Optional[str] = Form(None),
        cheque_no: Optional[str] = Form(None),
        cheque_bank: Optional[str] = Form(None),
        receipt: Optional[UploadFile] = File(None),
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> PaymentResponseSchema:
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]

    request = PilgrimPaymentBaseSchema(
        amount=amount,
        tracking_id=tracking_id,
        description=description,
        date=date,
        payment_category=payment_category,
        bank_info_id=bank_info_id,
        way_of_payment=way_of_payment,
        transfer_no=transfer_no,
        category="Payment",
        voucher_no=voucher_no,
        cheque_no=cheque_no,
        cheque_bank=cheque_bank
    )

    return await pilgrim_payment_service.create_payment_for_pilgrim(db, request, agency_name, receipt)


@private_router.get("/payment-info/pilgrim", response_model=PaginatedPaymentResponseForGroupLeader, tags=["payment"])
async def get_pilgrim_payment_info(
        db: AsyncSession = Depends(get_async_db),
        category: str | None = Query(None, description="Filter by payment category"),
        page: int = Query(1, ge=1),
        size: int = Query(100, ge=1),
        current_user: dict = Depends(get_current_pilgrim)
):
    tracking_id = current_user.get("tracking_id")
    if not tracking_id:
        raise HTTPException(status_code=400, detail="Tracking ID is missing in user context")

    return await pilgrim_payment_service.get_pilgrim_payments(
        db=db,
        tracking_id=tracking_id,
        category=category,
        page=page,
        size=size
    )


@public_router.get("/payment/{payment_id}", tags=["payment"])
async def get_payment_by_id(
        payment_id: int,
        db: AsyncSession = Depends(get_async_db),
):
    return await payment_service.get_payment_by_id(db, payment_id)

@private_router.get("/payment/{payment_id}", tags=["payment"])
async def get_payment_by_id(
        payment_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]

    return await payment_service.get_payment_by_id_for_update(db, payment_id, agency_name)

@private_router.get("/payable/{payable_id}", tags=["payment"])
async def get_payable_by_id(
        payable_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await pilgrim_payment_service.get_payable_by_id(db, payable_id, agency_name)

@private_router.get("/payable-report/{payable_id}", tags=["payment"])
async def get_payable_report_data(
        payable_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]

    return await pilgrim_payment_service.get_payable_report_data(db=db, payable_id=payable_id, agency_name=agency_name)
