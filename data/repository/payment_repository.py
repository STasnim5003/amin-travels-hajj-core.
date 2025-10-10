import random
import string
from typing import Optional, List

from fastapi import HTTPException, UploadFile
from sqlalchemy import insert, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.admin_user_model import AdminUserModel
from data.model.payment_model import PaymentModel
from infrastructure.schema.payment_schema import PaymentSchema, AgencyPaymentSchemaForGroupLeader


async def create_payable_for_group_leader(db: AsyncSession, payment_request: PaymentSchema, agency_name: str, receipt : Optional[List[UploadFile]]):
    try:
        # Generate an 8-character random alphanumeric transaction ID
        transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        # Prepare data for insertion
        payment_data = payment_request.model_dump(exclude_unset=True)
        payment_data.update({
            "transaction_id": transaction_id,
            "created_by": agency_name,
            "updated_by": agency_name,
            "no_of_hajji": len(payment_request.pilgrims_id),
            "receipt": receipt
        })

        # Insert into payment_info
        stmt = (
            insert(PaymentModel)
            .values(**payment_data)
            .returning(PaymentModel)
        )
        result = await db.execute(stmt)
        created_payment = result.scalar_one()

        group_leader_code = payment_data.get("group_leader")

        if group_leader_code:
            # Get current payable total for that group leader
            query = select(AdminUserModel).where(AdminUserModel.code == group_leader_code)
            res = await db.execute(query)
            admin_user = res.scalar_one_or_none()

            if admin_user:
                # Increase total_due by the payment amount
                prev_available_amount = admin_user.total_available_amount or 0
                payable_amount = payment_data["amount"]
                if payable_amount >= prev_available_amount:
                    new_available_amount = 0
                    new_total_due = admin_user.total_due +( payable_amount - prev_available_amount)
                else:
                    new_total_due = 0
                    new_available_amount = prev_available_amount -  payable_amount

                new_total_payable = (admin_user.total_payable or 0) + payment_data["amount"]
                total_available_amount = new_available_amount
                await db.execute(
                    update(AdminUserModel)
                    .where(AdminUserModel.code == group_leader_code)
                    .values(total_due=new_total_due)
                    .values(total_payable=new_total_payable)
                    .values(total_available_amount=total_available_amount)
                )

        await db.commit()
        return created_payment

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating payment record: {str(e)}")


async def create_payment_for_group_leader(db: AsyncSession, request: AgencyPaymentSchemaForGroupLeader,
                                          agency_name: str, receipt: Optional[List[dict]] = None):
    try:
        # Check payable
        payment_query = select(PaymentModel).where(PaymentModel.id == request.payable_id)
        payment_query_result = await db.execute(payment_query)
        payment_result = payment_query_result.scalar_one_or_none()
        if not payment_result:
            raise HTTPException(status_code=400, detail="Payable Id not found")

        # Check Group Leader
        admin_user = None
        if request.group_leader:
            query = select(AdminUserModel).where(AdminUserModel.code == request.group_leader)
            res = await db.execute(query)
            admin_user = res.scalar_one_or_none()

            if not admin_user:
                raise HTTPException(status_code=400, detail="Group Leader not found")
            if admin_user.agency_name != agency_name:
                raise HTTPException(status_code=400, detail="Agency Name does not match")

        transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        payment_data = request.model_dump(exclude_unset=True)
        payment_data.update({
            "transaction_id": transaction_id,
            "created_by": agency_name,
            "updated_by": agency_name,
            "payable_id": request.payable_id,
            "no_of_hajji": len(request.pilgrims_id),
            "receipt" : receipt
        })

        # Step 3: Insert into payment table
        stmt = (
            insert(PaymentModel)
            .values(**payment_data)
            .returning(PaymentModel)
        )

        result = await db.execute(stmt)
        created_payment = result.scalar_one()


        if admin_user:
            prev_due = admin_user.total_due or 0
            amount_paid = payment_data["amount"]
            if amount_paid >= prev_due:
                new_total_due = 0
                extra_amount = amount_paid - prev_due
            else:
                new_total_due = prev_due - amount_paid
                extra_amount = 0
            new_total_payment = (admin_user.total_payment or 0) + payment_data["amount"]
            new_total_available_amount = (admin_user.total_available_amount or 0) + extra_amount
            await db.execute(
                update(AdminUserModel)
                .where(AdminUserModel.code == request.group_leader)
                .values(total_due=new_total_due)
                .values(total_payment=new_total_payment)
                .values(total_available_amount=new_total_available_amount)
            )

        await db.commit()

        return created_payment

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating group leader payment: {str(e)}")


async def get_payments_by_group_leader(
        db: AsyncSession,
        group_leader: str,
        category: str | None,
        page: int,
        size: int
):
    try:
        query = select(PaymentModel).where(PaymentModel.group_leader == group_leader)

        if category:
            query = query.where(PaymentModel.category == category)

        # Count total rows before pagination
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(total_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.offset((page - 1) * size).limit(size)
        result = await db.execute(query)
        payments = result.scalars().all()

        query = (
            select(
                AdminUserModel.total_payable,
                AdminUserModel.total_payment,
                AdminUserModel.total_due,
                AdminUserModel.total_available_amount
            )
            .where(AdminUserModel.code == group_leader)
        )

        result = await db.execute(query)
        row = result.first()

        if not row:
            raise HTTPException(status_code=400, detail="Group leader not found")

        total_payable, total_payment, total_due, total_available_amount = row

        return payments, total, total_payable, total_payment, total_due, total_available_amount

    except Exception as e:
        raise Exception(f"Error fetching group leader payments: {str(e)}")


async def get_payments_by_agency(db: AsyncSession, agency_name: str, group_leader: str, category: str, page: int,
                                 size: int):
    try:
        query = select(PaymentModel).where(PaymentModel.created_by == agency_name)

        if category:
            query = query.where(PaymentModel.category == category)
        if group_leader:
            query = query.where(PaymentModel.group_leader == group_leader)

        # Count total rows before pagination
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(total_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.offset((page - 1) * size).limit(size)
        result = await db.execute(query)
        payments = result.scalars().all()

        return payments, total

    except Exception as e:
        raise Exception(f"Error fetching group leader payments: {str(e)}")
