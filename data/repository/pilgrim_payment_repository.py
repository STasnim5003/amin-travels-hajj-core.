import random
import string
from typing import Optional, List

from fastapi import UploadFile, HTTPException
from soupsieve import select
from sqlalchemy import insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.admin_user_model import AdminUserModel
from data.model.payment_model import PaymentModel
from data.model.pilgrim_data_model import PilgrimDataModel
from infrastructure.schema.payment_schema import PaymentSchema, PayableInfoUpdateSchema


async def create_payable_for_pilgrim(
        db: AsyncSession,
        payment_request: PaymentSchema,
        agency_name: str,
        receipt: Optional[List[UploadFile]]
):
    transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    # Prepare data for insertion
    payment_data = payment_request.model_dump(exclude_unset=True)
    payment_data.update({
        "transaction_id": transaction_id,
        "created_by": agency_name,
        "updated_by": agency_name,
        "receipt": receipt,
        "total_payable": payment_data.get("amount"),
        "total_due": payment_data.get("amount")
    })

    stmt = (
        insert(PaymentModel)
        .values(**payment_data)
        .returning(PaymentModel)
    )
    result = await db.execute(stmt)
    created_payment = result.scalar_one()
    return created_payment

async def create_payment_for_pilgrim(
        db: AsyncSession,
        payment_request: PaymentSchema,
        agency_name: str,
        receipt: Optional[List[UploadFile]]
):
    transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    # Prepare data for insertion
    payment_data = payment_request.model_dump(exclude_unset=True)
    payment_data.update({
        "transaction_id": transaction_id,
        "created_by": agency_name,
        "updated_by": agency_name,
        "receipt": receipt,
        "total_payment": payment_data.get("amount")
    })

    stmt = (
        insert(PaymentModel)
        .values(**payment_data)
        .returning(PaymentModel)
    )
    result = await db.execute(stmt)
    created_payment = result.scalar_one()
    return created_payment

async def update_pilgrim_payment_info(db: AsyncSession, payment_info: PayableInfoUpdateSchema):
    try:
        # Determine which model and column to use
        if payment_info.tracking_id:
            model = PilgrimDataModel
            id_column = PilgrimDataModel.tracking_id
            identifier = payment_info.tracking_id
        elif payment_info.group_leader_code:
            model = AdminUserModel
            id_column = AdminUserModel.code
            identifier = payment_info.group_leader_code
        else:
            raise HTTPException(status_code=400, detail="Either tracking_id or group_leader_code must be provided")

        # Build update statement dynamically
        stmt = (
            update(model)
            .where(id_column == identifier)
            .values(
                total_payable=payment_info.total_payable,
                total_available_amount=payment_info.total_available_amount,
                total_due=payment_info.total_due
            )
            .returning(model)
        )

        result = await db.execute(stmt)
        updated_record = result.scalar_one_or_none()

        if not updated_record:
            raise HTTPException(status_code=400, detail="Record not found")

        await db.commit()
        return updated_record

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating payment info: {str(e)}")


# async def get_payable_by_payable_id(db:AsyncSession, payable_id: int):
#     try:
#         stmt = (
#             select(PaymentModel).where(PaymentModel.id == payable_id)
#         )
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error getting payable info: {str(e)}")