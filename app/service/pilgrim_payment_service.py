from typing import Optional, List

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import pilgrim_payment_repository, file_repository, pilgrim_repository
from infrastructure.schema.payment_schema import PayableInfoUpdateSchema, PaymentSchema, PaymentResponseSchema, \
    PaginatedPaymentResponseForGroupLeader


async def create_payable_for_pilgrim(
        db: AsyncSession, payment_data: PaymentSchema, agency_name: str, receipt: Optional[List[UploadFile]]
) -> PaymentResponseSchema:
    if payment_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    pilgrim = None

    try:
        if payment_data.tracking_id:
            pilgrim = await pilgrim_repository.get_pilgrim_by_tracking_id(db, payment_data.tracking_id)

            if not pilgrim:
                raise HTTPException(status_code=400, detail="Pilgrim with tracking id not found")
        else:
            raise HTTPException(status_code=400, detail="Give valid tracking id for pilgrim payment")
    except Exception as e:
        raise e

    # upload receipt
    receipt_data = []
    if receipt:
        try:
            for file in receipt:
                receipt_resp = await file_repository.upload_file(file=file, name="receipt")
                receipt_data.append(receipt_resp.model_dump())
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"File upload failed: {str(e)}")

    try:
        result = await pilgrim_payment_repository.create_payable_for_pilgrim(db, payment_data, agency_name,
                                                                             receipt_data)

        if result:
            prev_available_amount = pilgrim.total_available_amount or 0
            payable_amount = payment_data.amount
            if payable_amount >= prev_available_amount:
                new_available_amount = 0
                new_total_due = pilgrim.total_due + (payable_amount - prev_available_amount)
            else:
                new_total_due = 0
                new_available_amount = prev_available_amount - payable_amount

            new_total_payable = (pilgrim.total_payable or 0) + payment_data.amount
            total_available_amount = new_available_amount

            payment_info = PayableInfoUpdateSchema(
                total_payable=new_total_payable,
                total_available_amount=total_available_amount,
                total_due=new_total_due,
                tracking_id=payment_data.tracking_id
            )
            response = await pilgrim_payment_repository.update_pilgrim_payment_info(db, payment_info)
            return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def create_payment_for_pilgrim(
        db: AsyncSession, payment_data: PaymentSchema, agency_name: str, receipt: Optional[List[UploadFile]]
):
    if payment_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    pilgrim = None

    try:
        if payment_data.tracking_id:
            pilgrim = await pilgrim_repository.get_pilgrim_by_tracking_id(db, payment_data.tracking_id)

            if not pilgrim:
                raise HTTPException(status_code=400, detail="Pilgrim with tracking id not found")
        else:
            raise HTTPException(status_code=400, detail="Give valid tracking id for pilgrim payment")
    except Exception as e:
        raise e

    # upload receipt
    receipt_data = []
    if receipt:
        try:
            for file in receipt:
                receipt_resp = await file_repository.upload_file(file=file, name="receipt")
                receipt_data.append(receipt_resp.model_dump())
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"File upload failed: {str(e)}")

    try:
        result = await pilgrim_payment_repository.create_payment_for_pilgrim(db, payment_data, agency_name,
                                                                             receipt_data)
        if result:
            prev_available_amount = pilgrim.total_available_amount or 0
            prev_due_amount = pilgrim.total_due or 0
            prev_total_amount = pilgrim.total_payment or 0
            curr_payment = payment_data.amount

            if curr_payment >= prev_due_amount:
                new_due_amount = 0
                new_available_amount = prev_available_amount + curr_payment - prev_due_amount
            else:
                new_due_amount = prev_due_amount - curr_payment
                new_available_amount = prev_available_amount
            new_total_amount = prev_total_amount + curr_payment

            payment_info = PayableInfoUpdateSchema(
                total_payment=new_total_amount,
                total_available_amount=new_available_amount,
                total_due=new_due_amount,
                tracking_id=payment_data.tracking_id
            )
            response = await pilgrim_payment_repository.update_pilgrim_payment_info(db, payment_info)
            return result
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
    ) = await pilgrim_payment_repository.get_payments_by_tracking_id(db, tracking_id, category, page, size)

    payment_list = [PaymentResponseSchema.model_validate(p) for p in payments]
    payables = [p for p in payment_list if p.payable_id is None]
    non_payables = [p for p in payment_list if p.payable_id is not None]

    # Map non-payables to their payables
    for payable in payables:
        related_payments = [p for p in non_payables if p.payable_id == payable.id]

        payable.payments = related_payments
        payable.total_payable = payable.amount
        payable.total_paid = sum(p.amount for p in related_payments)
        payable.total_due = max(payable.total_payable - payable.total_paid, 0)

    return PaginatedPaymentResponseForGroupLeader(
        payments=payables,
        page=page,
        size=size,
        total=total,
        total_payable=pilgrim_total_payable,
        total_payment=pilgrim_total_payment,
        total_due=pilgrim_total_due,
        total_available_amount=pilgrim_total_available_amount
    )
