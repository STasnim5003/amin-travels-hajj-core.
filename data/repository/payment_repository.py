import random
import string

from fastapi import HTTPException
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.admin_user_model import AdminUserModel
from data.model.payment_model import PaymentModel
from infrastructure.schema.payment_schema import PaymentSchema


async def create_payable_for_group_leader(db:AsyncSession, payment_request : PaymentSchema, agency_name : str):
    try:
        # Generate an 8-character random alphanumeric transaction ID
        transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        # Prepare data for insertion
        payment_data = payment_request.model_dump(exclude_unset=True)
        payment_data.update({
            "transaction_id": transaction_id,
            "status": "Unpaid",
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

                await db.execute(
                    update(AdminUserModel)
                    .where(AdminUserModel.code == group_leader_code)
                    .values(total_due=new_total_due)
                )

        await db.commit()
        return created_payment

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating payment record: {str(e)}")