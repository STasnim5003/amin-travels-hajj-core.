import random
import string
from typing import Optional, List

from fastapi import UploadFile, HTTPException
from sqlalchemy import insert, update, select, func, desc
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
    payable_id = payment_data.get("payable_id")
    try:
        payable = await get_payable_by_payable_id(db, payable_id)

        new_due_amount = payable.total_due - payment_data.get("amount")
        new_due_amount = max(new_due_amount, 0)

        new_total_payment = payment_data.get("amount") + payable.total_payment

        payment_data.update({
            "transaction_id": transaction_id,
            "created_by": agency_name,
            "updated_by": agency_name,
            "receipt": receipt,
            "total_payment": new_total_payment,
            "total_due": new_due_amount
        })

        stmt = (
            insert(PaymentModel)
            .values(**payment_data)
            .returning(PaymentModel)
        )
        result = await db.execute(stmt)

        stmt = (
            update(PaymentModel)
            .values(total_payment=new_total_payment, total_due=new_due_amount)
            .where(PaymentModel.id == payable_id)
        )
        res = await db.execute(stmt)
        created_payment = result.scalar_one()
        return created_payment
    except Exception as e:
        raise e

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
        if payment_info.total_payable:
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
        else:
            stmt = (
                update(model)
                .where(id_column == identifier)
                .values(
                    total_payment=payment_info.total_payment,
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


async def get_payable_by_payable_id(db: AsyncSession, payable_id: int):
    try:
        stmt = select(PaymentModel).where(PaymentModel.id == payable_id)
        result = await db.execute(stmt)
        payable = result.scalar_one_or_none()

        if not payable:
            raise HTTPException(status_code=404, detail=f"Payable with ID {payable_id} not found")

        return payable

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error retrieving payable: {str(e)}")

async def get_payments_by_tracking_id(
        db: AsyncSession,
        tracking_id: str,
        category: str | None,
        page: int,
        size: int
):
    try:
        query = select(PaymentModel).where(PaymentModel.tracking_id == tracking_id)

        if category:
            query = query.where(PaymentModel.category == category)

        # Count total rows before pagination
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(total_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.order_by(desc(PaymentModel.id)).offset((page - 1) * size).limit(size)
        result = await db.execute(query)
        payments = result.scalars().all()

        query = (
            select(
                PilgrimDataModel.total_payable,
                PilgrimDataModel.total_payment,
                PilgrimDataModel.total_due,
                PilgrimDataModel.total_available_amount
            )
            .where(PilgrimDataModel.tracking_id == tracking_id)
        )

        result = await db.execute(query)
        row = result.first()

        if not row:
            raise HTTPException(status_code=400, detail="Group leader not found")

        total_payable, total_payment, total_due, total_available_amount = row

        return payments, total, total_payable, total_payment, total_due, total_available_amount

    except Exception as e:
        raise Exception(f"Error fetching group leader payments: {str(e)}")