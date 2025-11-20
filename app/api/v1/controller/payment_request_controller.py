import fastapi
from fastapi import Depends, HTTPException, Form, UploadFile, File

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import payment_request_service
from data.db.db_config import get_async_db
from infrastructure.schema.payment_request_schema import PaymentRequestResponse, PaymentRequestB2BBase, \
    PaymentRequestListResponseSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private", tags=["payment-request"])

@private_router.post("/payment-request", response_model=PaymentRequestResponse)
async def payment_request(
        payment_way: str = Form(...),
        money_receipt_payment_slip_file: UploadFile = File(None),
        reference_number: str = Form(None),
        transaction_id: str = Form(None),
        money_receipt_number:str = Form(None),
        status:str = Form(None),
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]

    request = {
        'payment_way': payment_way,
        'reference_number': reference_number,
        'transaction_id': transaction_id,
        'money_receipt_number': money_receipt_number,
        'status': status,
        'agency_name': agency_name,
        'created_by': agency_name,
        'updated_by': agency_name,
    }
    return await payment_request_service.create_payment_request(db, request, money_receipt_payment_slip_file)

@private_router.get("/payment-request", response_model=PaymentRequestListResponseSchema)
async def get_payment_requests(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]

    return await payment_request_service.get_payment_requests(db, agency_name)

@private_router.put("/payment-request", response_model=PaymentRequestResponse)
async def update_payment_request(
        id: int = Form(...),
        payment_way: str = Form(None),
        money_receipt_payment_slip_file: UploadFile = File(None),
        reference_number: str = Form(None),
        transaction_id: str = Form(None),
        money_receipt_number:str = Form(None),
        status:str = Form(None),
        is_active:bool = Form(None),
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]

    request = {
        'id':id,
        'payment_way': payment_way,
        'reference_number': reference_number,
        'transaction_id': transaction_id,
        'money_receipt_number': money_receipt_number,
        'status': status,
        'agency_name': agency_name,
        'updated_by': agency_name,
        'is_active': is_active,
    }
    return await payment_request_service.update_payment_request(db=db, request_dict = request, money_receipt_payment_slip_file = money_receipt_payment_slip_file)

@private_router.get("/payment-request/{payment_request_id}", response_model=PaymentRequestResponse)
async def get_payment_request(
        payment_request_id:int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user['agency_name']

    return await payment_request_service.get_payment_request_by_id(db, payment_request_id, agency_name)

@private_router.delete("/payment-request/{payment_request_id}")
async def delete_payment_request(
        payment_request_id:int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]

    return await payment_request_service.delete_payment_request(db, payment_request_id, agency_name)