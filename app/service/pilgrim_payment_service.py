import random
import string

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import pilgrim_payment_repository, pilgrim_repository
from infrastructure.schema.payment_schema import PayableInfoUpdateSchema, PaymentResponseSchema, \
    PaginatedPaymentResponseForGroupLeader, PilgrimPayableBaseSchema, PilgrimPaymentBaseSchema


async def create_payable_for_pilgrim(
        db: AsyncSession, payment_data: PilgrimPayableBaseSchema, agency_name: str
) -> PaymentResponseSchema:
    if payment_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    try:
        pilgrim = await pilgrim_repository.get_pilgrim_by_tracking_id(db, payment_data.tracking_id)
        if not pilgrim or pilgrim.group_name != agency_name:
            raise HTTPException(status_code=400, detail="Pilgrim with tracking id not found")

    except Exception as e:
        raise e

    # Update Pilgrim TK Info
    pilgrim_prev_total_payable = pilgrim.total_payable or 0
    pilgrim_prev_total_payment = pilgrim.total_payment or 0
    prev_actual_payable = pilgrim.actual_payable or 0

    new_total_payable = pilgrim_prev_total_payable + payment_data.amount
    new_total_due = max(0, new_total_payable - pilgrim_prev_total_payment)
    new_total_available_amount = max(0, pilgrim_prev_total_payment - new_total_payable)
    new_actual_payable = prev_actual_payable + payment_data.amount

    payable_info = PayableInfoUpdateSchema(
        tracking_id=payment_data.tracking_id,
        total_payable=new_total_payable,
        total_due=new_total_due,
        total_available_amount=new_total_available_amount,
        actual_payable=new_actual_payable
    )

    # Create Payable Info
    transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    payment_request_dict = payment_data.model_dump(exclude_unset=True)
    payment_request_dict.update({
        "transaction_id": transaction_id,
        "created_by": agency_name,
        "updated_by": agency_name
    })

    try:
        result = await pilgrim_payment_repository.create_payable_for_pilgrim(db, payment_request_dict, payable_info)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def create_payment_for_pilgrim(
        db: AsyncSession, payment_data: PilgrimPaymentBaseSchema, agency_name: str
):
    if payment_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    try:
        pilgrim = await pilgrim_repository.get_pilgrim_by_tracking_id(db, payment_data.tracking_id)
        if not pilgrim or pilgrim.group_name != agency_name:
            raise HTTPException(status_code=400, detail="Pilgrim with tracking id not found")

    except Exception as e:
        raise e

    prev_total_payable = pilgrim.total_payable or 0
    prev_total_payment = pilgrim.total_payment or 0

    new_total_payment = prev_total_payment + payment_data.amount
    new_total_due = max(0, prev_total_payable - new_total_payment)
    new_available_amount = max(0, new_total_payment - prev_total_payable)

    payment_info = PayableInfoUpdateSchema(
        total_payment=new_total_payment,
        total_available_amount=new_available_amount,
        total_due=new_total_due,
        tracking_id=payment_data.tracking_id
    )

    transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    payment_request_dict = payment_data.model_dump(exclude_unset=True)
    payment_request_dict.update({
        "transaction_id": transaction_id,
        "created_by": agency_name,
        "updated_by": agency_name
    })

    try:
        result = await pilgrim_payment_repository.create_payment_for_pilgrim(db, payment_request_dict, payment_info)
        return PaymentResponseSchema.model_validate(result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def get_pilgrim_payments(
        db,
        tracking_id: str,
        category: str | None,
        page: int,
        size: int
):
    (
        payments,
        total,
        pilgrim_total_payable,
        pilgrim_total_payment,
        pilgrim_total_due,
        pilgrim_total_available_amount
    ) = await pilgrim_payment_repository.get_payments_by_tracking_id(db, tracking_id, page, size)

    return PaginatedPaymentResponseForGroupLeader(
        grouped_payments=payments,
        page=page,
        size=size,
        total=total,
        total_payable=pilgrim_total_payable,
        total_payment=pilgrim_total_payment,
        total_due=pilgrim_total_due,
        total_available_amount=pilgrim_total_available_amount
    )
