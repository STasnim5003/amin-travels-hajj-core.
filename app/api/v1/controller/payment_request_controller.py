import fastapi
from fastapi import Depends, HTTPException, Form, UploadFile, File

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import payment_request_service
from data.db.db_config import get_async_db
from infrastructure.schema.payment_request_schema import PaymentRequestResponse, PaymentRequestB2BBase, \
    PaymentRequestListResponseSchema, PaymentRequestCreateSchema, PaymentRequestUpdateSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private", tags=["payment-request"])

@private_router.post("/payment-request", response_model=PaymentRequestResponse)
async def payment_request(
        request : PaymentRequestCreateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await payment_request_service.create_payment_request(db=db, request=request,agency_name=agency_name)

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
        request : PaymentRequestUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]

    return await payment_request_service.update_payment_request(db=db, request = request, agency_name=agency_name)

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