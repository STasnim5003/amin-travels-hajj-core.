import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user, get_current_admin_user
from app.service import payment_service
from data.db.db_config import get_async_db
from infrastructure.schema.payment_schema import PaymentResponseSchema, PaymentSchema, GroupLeaderPaymentSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")

@private_router.post("/group-leader/create-payable", response_model=PaymentResponseSchema, tags=["payment"])
async def create_payable_for_group_leader(
        payment_request : PaymentSchema,
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
        request_schema : GroupLeaderPaymentSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_admin_user)
) -> PaymentResponseSchema:
    if current_user["role"] != "GROUP_LEADER":
        raise HTTPException(status_code=403, detail="Unauthorized")
    group_leader = current_user["code"]
    return await payment_service.create_group_leader_payment(db, request_schema, group_leader)



