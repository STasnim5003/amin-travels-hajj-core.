from typing import Optional, List

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import pilgrim_payment_repository, file_repository, pilgrim_repository
from infrastructure.schema.payment_schema import PayableInfoUpdateSchema, PaymentSchema, PaymentResponseSchema


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
