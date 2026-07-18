from typing import Optional

import fastapi
from fastapi import Depends, HTTPException, Query, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.controller.pilgrim_controller import public_router
from app.core.middleware.middleware import get_current_user, get_current_admin_user, get_current_pilgrim
from app.core.utils.authorize_api import check_agency_or_staff_user
from app.service import payment_service, pilgrim_payment_service
from data.db.db_config import get_async_db
from infrastructure.schema.payment_schema import PaymentResponseSchema, PaginatedPaymentResponseForGroupLeader, \
    PaginatedPaymentResponseForAgency, GroupLeaderPayableBaseSchema, PilgrimPayableBaseSchema, \
    PilgrimPaymentBaseSchema, \
    GroupLeaderPaymentBaseSchema, PayableUpdateSchema, PaymentUpdateSchema, PaymentLedgerSchema, \
    PilgrimsPaymentSummaryListSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")


@private_router.post("/group-leader/create-payable", tags=["payment"])
async def create_payable_for_group_leader(
        request: GroupLeaderPayableBaseSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    username = current_user["username"]
    return await payment_service.create_payable_for_group_leader(db, request, agency_name, username)


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
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user['agency_name']
    username = current_user['username']
    tracking_ids = []
    if pilgrims_tracking_id:
        tracking_ids = [tid.strip() for tid in pilgrims_tracking_id.split(',')]

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
    return await payment_service.create_group_leader_payment(db, request_schema, agency_name, receipt, username)


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


@private_router.get("/agency/pilgrims-payment-info", tags=["payment"])
async def get_agency_pilgrims_payment_info(
        hajj_year: int = Query(..., description="Hajj year to filter pilgrims"),
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]

    # return await payment_service.get_agency_payments(db, agency_name)
    return await payment_service.get_agency_pilgrims_payment_info(db, agency_name, hajj_year)


@private_router.put("/update-payable", response_model=PaymentResponseSchema, tags=["payment"])
async def update_payable(
        payable_request: PayableUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> PaymentResponseSchema:
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    username = current_user['username']
    return await payment_service.update_payable(db, payable_request, agency_name, username)


@private_router.put("/update-payment", tags=["payment"])
async def update_payment(
        db: AsyncSession = Depends(get_async_db),
        payment_id: int = Form(...),
        group_leader: Optional[str] = Form(None),
        tracking_id: Optional[str] = Form(None),
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
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    username = current_user['username']
    tracking_ids = []
    if pilgrims_tracking_id:
        tracking_ids = [tid.strip() for tid in pilgrims_tracking_id.split(',')]

    payment_update_schema = PaymentUpdateSchema(
        payment_id=payment_id,
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
        pilgrims_tracking_id=tracking_ids
    )

    return await pilgrim_payment_service.update_payment(db=db, payment_update_schema=payment_update_schema,
                                                        agency_name=agency_name, receipt=receipt, username=username)


@private_router.post("/pilgrim/create-payable", response_model=PaymentResponseSchema, tags=["payment"])
async def create_payable_for_pilgrim(
        request: PilgrimPayableBaseSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> PaymentResponseSchema:
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    username = current_user['username']
    result = await pilgrim_payment_service.create_payable_for_pilgrim(db, request, agency_name, username)
    return PaymentResponseSchema.model_validate(result)


@private_router.post("/pilgrim/create-payment", response_model=PaymentResponseSchema, tags=["payment"])
async def create_payment_for_pilgrim(
        amount: int = Form(...),
        tracking_id: str = Form(None),
        nid: str = Form(None),
        passport_no: str = Form(None),
        pilgrim_name: str = Form(None),
        hajj_year: int = Form(None),
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
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    username = current_user['username']
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
        cheque_bank=cheque_bank,
        nid=nid,
        passport_no=passport_no,
        pilgrim_name=pilgrim_name,
        hajj_year=hajj_year
    )

    return await pilgrim_payment_service.create_payment_for_pilgrim(db, request, agency_name, receipt, username)


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


@private_router.get("/payment-info-for-receipt/{payment_id}", tags=["payment"])
async def get_payment_by_id_for_receipt(
        payment_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await payment_service.get_payment_by_id_for_receipt(db, payment_id, agency_name)


@private_router.get("/payment/{payment_id}", tags=["payment"])
async def get_payment_by_id(
        payment_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]

    return await payment_service.get_payment_by_id_for_update(db, payment_id, agency_name)


@private_router.get("/payable/{payable_id}", tags=["payment"])
async def get_payable_by_id(
        payable_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await pilgrim_payment_service.get_payable_by_id(db, payable_id, agency_name)


@private_router.get("/payable-report/{payable_id}", tags=["payment"])
async def get_payable_report_data(
        payable_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user),
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]

    return await pilgrim_payment_service.get_payable_report_data(db=db, payable_id=payable_id, agency_name=agency_name)


@private_router.get("/payment-ledger", tags=["payment"])
async def get_payment_ledger(
        tracking_id: Optional[str] = None,
        group_leader: Optional[str] = None,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]

    result = await pilgrim_payment_service.get_payment_ledger(db, tracking_id, group_leader, agency_name)
    return PaymentLedgerSchema.model_validate(result)


@private_router.get("/pilgrim-payment-summary-list", response_model=PilgrimsPaymentSummaryListSchema, tags=["payment"])
async def get_pilgrim_payment_summary_list(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]

    return await pilgrim_payment_service.get_pilgrims_payment_summary(db=db, agency_name=agency_name)


@private_router.get("/agency/pilgrims-for-payment", tags=["payment"])
async def get_agency_pilgrims_for_payment(
        hajj_year: int = Query(..., description="Hajj year to filter pilgrims"),
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]

    return await payment_service.get_agency_pilgrims_for_payment(db=db, agency_name=agency_name, hajj_year=hajj_year)