import random
import string

from fastapi import HTTPException
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.admin_user_model import AdminUserModel
from data.model.payment_model import PaymentModel
from infrastructure.schema.payment_schema import PaymentSchema, GroupLeaderPaymentSchema


async def create_payable_for_group_leader(db:AsyncSession, payment_request : PaymentSchema, agency_name : str):
    try:
        # Generate an 8-character random alphanumeric transaction ID
        transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        # Prepare data for insertion
        payment_data = payment_request.model_dump(exclude_unset=True)
        payment_data.update({
            "transaction_id": transaction_id,
            "created_by": agency_name,
            "updated_by": agency_name,
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
                new_total_due = (admin_user.total_due or 0) + payment_data["amount"]
                new_total_payable = (admin_user.total_payable or 0) + payment_data["amount"]
                await db.execute(
                    update(AdminUserModel)
                    .where(AdminUserModel.code == group_leader_code)
                    .values(total_due=new_total_due)
                    .values(total_payable=new_total_payable)
                )

        await db.commit()
        payment_dict = created_payment.__dict__.copy()
        payment_dict["no_of_hajji"] = len(payment_request.pilgrims_id)
        return payment_dict

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating payment record: {str(e)}")

async def create_payment_of_group_leader(db:AsyncSession, request : GroupLeaderPaymentSchema, group_leader : str):
    try:
        transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        payment_data = request.model_dump(exclude_unset=True)
        payment_data.update({
            "transaction_id": transaction_id,
            "group_leader": group_leader,
            "created_by": group_leader,
            "updated_by": group_leader,
        })

        # Step 3: Insert into payment table
        stmt = (
            insert(PaymentModel)
            .values(**payment_data)
            .returning(PaymentModel)
        )

        result = await db.execute(stmt)
        created_payment = result.scalar_one()
        if group_leader:
            query = select(AdminUserModel).where(AdminUserModel.code == group_leader)
            res = await db.execute(query)
            admin_user = res.scalar_one_or_none()

            if admin_user:
                new_total_due = (admin_user.total_due or 0) - payment_data["amount"]
                new_total_payment = (admin_user.total_payment or 0) + payment_data["amount"]
                await db.execute(
                    update(AdminUserModel)
                    .where(AdminUserModel.code == group_leader)
                    .values(total_due=new_total_due)
                    .values(total_payment=new_total_payment)
                )

        await db.commit()

        payment_dict = created_payment.__dict__.copy()
        payment_dict["no_of_hajji"] = len(request.pilgrims_id)
        return payment_dict

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating group leader payment: {str(e)}")