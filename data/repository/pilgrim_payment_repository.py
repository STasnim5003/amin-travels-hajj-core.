import random
import string
from datetime import datetime
from typing import Optional, List

from fastapi import UploadFile, HTTPException
from sqlalchemy import insert, update, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.admin_user_model import AdminUserModel
from data.model.payment_model import PaymentModel
from data.model.pilgrim_data_model import PilgrimDataModel
from infrastructure.schema.payment_schema import PaymentSchema, PayableInfoUpdateSchema


async def create_payable_for_pilgrim(
    db: AsyncSession,
    payment_request: PaymentSchema,
    agency_name: str,
    receipt: Optional[List[UploadFile]],
    pilgrim_prev_total_payable: int,
    pilgrim_prev_total_payment: int,
):
    transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    payment_data = payment_request.model_dump(exclude_unset=True)
    payment_data.update({
        "transaction_id": transaction_id,
        "created_by": agency_name,
        "updated_by": agency_name,
        "receipt": receipt
    })

    try:
        # Create Payable
        stmt = (
            insert(PaymentModel)
            .values(**payment_data)
            .returning(PaymentModel)
        )
        result = await db.execute(stmt)
        created_payment = result.scalar_one()

        # Update Payment Info for Pilgrim
        new_total_payable = pilgrim_prev_total_payable + payment_request.amount
        new_total_due = max(0, new_total_payable - pilgrim_prev_total_payment)
        new_available_amount = max(0, pilgrim_prev_total_payment - new_total_payable)

        update_stmt = (
            update(PilgrimDataModel)
            .where(PilgrimDataModel.tracking_id == payment_request.tracking_id)
            .values(
                total_payable=new_total_payable,
                total_due=new_total_due,
                total_available_amount=new_available_amount,
                updated_by=agency_name
            )
        )
        await db.execute(update_stmt)

        await db.commit()

        return created_payment
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


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


async def update_payment_info(db: AsyncSession, payment_info: PayableInfoUpdateSchema):
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
            raise HTTPException(status_code=400, detail=f"Payable with ID {payable_id} not found")

        return payable

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error retrieving payable: {str(e)}")


async def get_payments_by_tracking_id(
        db: AsyncSession,
        tracking_id: str,
        page: int = 1,
        size: int = 100
):
    try:
        offset = (page - 1) * size

        query = text("""
            SELECT
                p.id AS id,
                p.description AS description,
                p.date AS date,
                p.amount AS amount,
                p.category AS category,
                p.total_payment AS total_paid,
                p.total_due AS total_due,
                p.tracking_id,
                p.group_leader,
                p.transaction_id AS transaction_id,
                p.created_at AS created_at,
                p.created_by AS created_by,
                p.updated_at AS updated_at,
                p.updated_by AS updated_by,
                pd.total_payable AS pilgrim_total_payable,
                pd.total_payment AS pilgrim_total_payment,
                pd.total_due AS pilgrim_total_due,
                pd.total_available_amount AS pilgrim_total_available_amount,
                COALESCE(p.receipt, '[]'::json) AS receipt,
                COALESCE(
                    json_agg(
                        json_build_object(
                            'id', c.id,
                            'description', c.description,
                            'date', c.date,
                            'amount', c.amount,
                            'category', c.category,
                            'tracking_id', c.tracking_id,
                            'payable_id', c.payable_id,
                            'transaction_id', c.transaction_id,
                            'created_at', c.created_at,
                            'created_by', c.created_by,
                            'updated_at', c.updated_at,
                            'updated_by', c.updated_by,
                            'receipt', COALESCE(c.receipt, '[]'::json),
                            'total_payable', c.total_payable,
                            'total_paid', c.total_payment,
                            'total_due', c.total_due
                        )
                    ) FILTER (WHERE c.id IS NOT NULL),
                    '[]'
                ) AS payments
            FROM core.payment p
            LEFT JOIN core.payment c
                ON c.payable_id = p.id AND c.category = 'Payment'
            LEFT JOIN core.pilgrim_data pd
                ON pd.tracking_id = p.tracking_id
            WHERE p.category = 'Payable' AND p.tracking_id = :tracking_id
            GROUP BY p.id, pd.tracking_id, pd.total_payable, pd.total_available_amount, pd.total_due, pd.total_payment
            ORDER BY p.id DESC
            LIMIT :size OFFSET :offset;
        """)

        result = await db.execute(
            query,
            {"tracking_id": tracking_id, "size": size, "offset": offset}
        )

        payments = result.mappings().all()  # returns a list of dict-like rows

        if not payments:
            raise HTTPException(status_code=400, detail="No payments found for this tracking ID")

        total_query = text("""
                    SELECT COUNT(*) FROM core.payment
                    WHERE tracking_id = :tracking_id
                    AND category = 'Payable'
                """)
        total_result = await db.execute(total_query, {"tracking_id": tracking_id})
        total = total_result.scalar() or 0

        first = payments[0]
        pilgrim_total_payable = first["pilgrim_total_payable"]
        pilgrim_total_payment = first["pilgrim_total_payment"]
        pilgrim_total_due = first["pilgrim_total_due"]
        pilgrim_total_available_amount = first["pilgrim_total_available_amount"]

        return payments, total, pilgrim_total_payable, pilgrim_total_payment, pilgrim_total_due, pilgrim_total_available_amount

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


