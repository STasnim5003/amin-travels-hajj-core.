from typing import List, Optional

from fastapi import UploadFile, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.admin_user_model import AdminUserModel
from data.repository import payment_repository, file_repository, admin_user_repository, pilgrim_payment_repository
from infrastructure.schema.payment_schema import PaymentSchema, PaginatedPaymentResponseForGroupLeader, \
    PaginatedPaymentResponseForAgency, AgencyPaymentSchemaForGroupLeader, PayableInfoUpdateSchema


async def create_payable_for_group_leader(db: AsyncSession, payment_request: PaymentSchema, agency_name: str,
                                          receipt: Optional[List[UploadFile]]):
    if payment_request.amount < 0:
        raise HTTPException(status_code=400, detail="Amount should be positive")

    #check group leader
    try:
        if payment_request.group_leader:
            existing_group_leader = await admin_user_repository.get_admin_user_by_code(db, payment_request.group_leader)
            if not existing_group_leader:
                raise HTTPException(status_code=400, detail="Group leader does not exist")
        else:
            raise HTTPException(status_code=400, detail="Group Leader is empty")
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
        result = await payment_repository.create_payable_for_group_leader(db, payment_request, agency_name, receipt_data)

        # update group leader payment info
        if result:
            prev_available_amount = existing_group_leader.total_available_amount or 0
            payable_amount = payment_request.amount

            if payable_amount >= prev_available_amount:
                new_available_amount = 0
                new_total_due = existing_group_leader.total_due + (payable_amount - prev_available_amount)
            else:
                new_total_due = 0
                new_available_amount = prev_available_amount - payable_amount

            new_total_payable = (existing_group_leader.total_payable or 0) + payment_request.amount
            total_available_amount = new_available_amount

            payment_info = PayableInfoUpdateSchema(
                total_payable=new_total_payable,
                total_available_amount=total_available_amount,
                total_due=new_total_due,
                group_leader_code=payment_request.group_leader
            )
            response = await pilgrim_payment_repository.update_payment_info(db, payment_info)
            return result
    except Exception as e:
        raise e


async def create_group_leader_payment(db: AsyncSession, request: AgencyPaymentSchemaForGroupLeader, agency_name: str,
                                      receipt: List[UploadFile] = None):
    if request.amount < 0:
        raise HTTPException(status_code=400, detail="Amount should be positive")

    receipt_data = []

    try:
        payable_id = request.payable_id
        group_leader = request.group_leader
        payable = await pilgrim_payment_repository.get_payable_by_payable_id(db, payable_id)
        if not payable:
            raise HTTPException(status_code=400, detail="Payable does not exist")

        new_due_amount = payable.total_due - request.amount
        new_due_amount = max(new_due_amount, 0)

        new_total_payment = request.amount + payable.total_payment

        admin_user = await admin_user_repository.get_admin_user_by_code(db, group_leader)
        if not admin_user:
            raise HTTPException(status_code=400, detail="Group leader does not exist")

        if admin_user.agency_name != agency_name:
            raise HTTPException(status_code=400, detail="Agency name is invalid")

    except Exception as e:
        raise e

    if receipt:
        try:
            for file in receipt:
                receipt_resp = await file_repository.upload_file(file=file, name="receipt")
                receipt_data.append(receipt_resp.model_dump())
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"File upload failed: {str(e)}")

    try:
        result = await payment_repository.create_payment_for_group_leader(db, request, agency_name,
                                                                          new_total_payment, new_due_amount,
                                                                          receipt_data)
        if result:
            prev_available_amount = admin_user.total_available_amount or 0
            prev_due_amount = admin_user.total_due or 0
            prev_total_amount = admin_user.total_payment or 0
            curr_payment = request.amount

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
                group_leader_code=request.group_leader
            )
            response = await pilgrim_payment_repository.update_payment_info(db, payment_info)
            return result
    except Exception as e:
        raise e


async def get_group_leader_payments(
        db,
        group_leader: str,
        category: str | None,
        page: int,
        size: int
):
    (
        payments,
        total,
        group_leader_total_payable,
        group_leader_total_payment,
        group_leader_total_due,
        group_leader_total_available_amount
    ) = await payment_repository.get_payments_by_group_leader(db, group_leader, category, page, size)

    return PaginatedPaymentResponseForGroupLeader(
        payments=payments,
        page=page,
        size=size,
        total=total,
        total_payable=group_leader_total_payable,
        total_payment=group_leader_total_payment,
        total_due=group_leader_total_due,
        total_available_amount=group_leader_total_available_amount
    )


async def get_agency_payments(
        db,
        agency_name: str,
        group_leader: str | None,
        tracking_id: str | None,
        category: str | None,
        page: int,
        size: int
):
    (
        payments,
        total
    ) = await payment_repository.get_payments_by_agency(db, agency_name, group_leader, tracking_id, category, page,
                                                        size)

    return PaginatedPaymentResponseForAgency(
        payments=payments,
        page=page,
        size=size,
        total=total
    )


async def update_payable(
        db: AsyncSession,
        payable_id: int,
        payment_data: dict,
        agency_name: str
):
    existing_payment = await payment_repository.get_by_id(db, payable_id)

    if existing_payment.created_by != agency_name:
        raise HTTPException(status_code=403, detail="Unauthorized to update this payable")

    filtered_data = {k: v for k, v in payment_data.items() if v is not None}

    if not filtered_data:
        raise HTTPException(status_code=400, detail="No valid fields provided to update")

    if "amount" in filtered_data:
        new_amount = filtered_data["amount"]
        old_amount = existing_payment.amount or 0

        # Only recalculate if the amount actually changed
        if new_amount != old_amount:
            group_leader_code = existing_payment.group_leader

            if group_leader_code:
                query = select(AdminUserModel).where(AdminUserModel.code == group_leader_code)
                res = await db.execute(query)
                admin_user = res.scalar_one_or_none()

                if admin_user:
                    # Reverse the old amount effect first
                    prev_available_amount = admin_user.total_available_amount or 0
                    prev_due = admin_user.total_due or 0
                    prev_total_payable = admin_user.total_payable or 0

                    # Subtract old amount first
                    prev_total_payable -= old_amount
                    if prev_available_amount >= old_amount:
                        prev_available_amount -= old_amount
                    else:
                        diff = old_amount - prev_available_amount
                        prev_due = max(prev_due - diff, 0)
                        prev_available_amount = 0

                    # Now add the new amount
                    if new_amount >= prev_available_amount:
                        new_available_amount = 0
                        new_total_due = prev_due + (new_amount - prev_available_amount)
                    else:
                        new_total_due = prev_due
                        new_available_amount = prev_available_amount - new_amount

                    new_total_payable = prev_total_payable + new_amount

                    await db.execute(
                        update(AdminUserModel)
                        .where(AdminUserModel.code == group_leader_code)
                        .values(
                            total_due=new_total_due,
                            total_payable=new_total_payable,
                            total_available_amount=new_available_amount,
                        )
                    )

    updated_payment = await payment_repository.update_payable(db, payable_id, filtered_data)
    return updated_payment
