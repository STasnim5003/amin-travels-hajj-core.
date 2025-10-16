import random
import string
from typing import List

from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import payment_repository, file_repository, admin_user_repository, pilgrim_payment_repository, \
    pilgrim_repository, payment_repository_multiple_pilgrims
from infrastructure.schema.payment_schema import PaginatedPaymentResponseForGroupLeader, \
    PaginatedPaymentResponseForAgency, AgencyPaymentSchemaForGroupLeader, PayableInfoUpdateSchema, \
    GroupLeaderPayableBaseSchema


async def create_payable_for_group_leader(db: AsyncSession, payment_request: GroupLeaderPayableBaseSchema,
                                          agency_name: str):
    if payment_request.amount < 0:
        raise HTTPException(status_code=400, detail="Amount should be positive")

    # check group leader
    try:
        if payment_request.group_leader:
            existing_group_leader = await admin_user_repository.get_admin_user_by_code(db, payment_request.group_leader)
            if not existing_group_leader:
                raise HTTPException(status_code=400, detail="Group leader does not exist")
        else:
            raise HTTPException(status_code=400, detail="Group Leader is empty")
    except Exception as e:
        raise e

    try:
        if existing_group_leader.is_payment_distributed:
            result =  await payment_repository_multiple_pilgrims.create_payable_for_multiple_pilgrims(db, payment_request, agency_name)
            return result
        else:
            new_total_payable = (existing_group_leader.total_payable or 0) + payment_request.amount
            prev_payment = existing_group_leader.total_payment

            new_total_available = max(0, prev_payment - new_total_payable)
            new_total_due = max(0, new_total_payable - prev_payment)

            payable_info = PayableInfoUpdateSchema(
                total_payable=new_total_payable,
                total_available_amount=new_total_available,
                total_due=new_total_due,
                group_leader_code=payment_request.group_leader
            )

            # Generate an 8-character random alphanumeric transaction ID
            transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

            payment_data = payment_request.model_dump(exclude_unset=True)
            payment_data.update({
                "transaction_id": transaction_id,
                "created_by": agency_name,
                "updated_by": agency_name,
                "no_of_hajji": len(payment_request.pilgrims_tracking_id)
            })

            result = await payment_repository.create_payable_for_group_leader(db, payment_data, payable_info, agency_name)
            return result
    except Exception as e:
        raise e


async def create_group_leader_payment(db: AsyncSession, request: AgencyPaymentSchemaForGroupLeader, agency_name: str,
                                      receipt: List[UploadFile] = None):
    if request.amount < 0:
        raise HTTPException(status_code=400, detail="Amount should be positive")

    receipt_data = []

    try:
        # Check Payable
        payable_id = request.payable_id
        group_leader = request.group_leader
        payable = await pilgrim_payment_repository.get_payable_by_payable_id(db, payable_id)
        if not payable:
            raise HTTPException(status_code=400, detail="Payable does not exist")

        # Update Payable amount
        new_due_amount = payable.total_due - request.amount
        new_due_amount = max(new_due_amount, 0)

        new_total_payment = request.amount + payable.total_payment

        # Check Group Leader & Agency
        admin_user = await admin_user_repository.get_admin_user_by_code(db, group_leader)
        if not admin_user:
            raise HTTPException(status_code=400, detail="Group leader does not exist")

        if admin_user.agency_name != agency_name:
            raise HTTPException(status_code=400, detail="Agency name is invalid")

    except Exception as e:
        raise e

    # Upload Receipt
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
        # Adjust Group Leader Payment
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

            # Fix the Payable itself
            payable_due_itself = 0
            if new_amount >= existing_payment.total_payment:
                payable_due_itself = new_amount - existing_payment.total_payment

            filtered_data.update({
                "total_payable": new_amount,
                "total_due": payable_due_itself
            })

            group_leader_code = existing_payment.group_leader
            tracking_id = existing_payment.tracking_id
            user = None
            if group_leader_code:
                user = await admin_user_repository.get_admin_user_by_code(db, group_leader_code)

            elif tracking_id:
                user = await pilgrim_repository.get_pilgrim_by_tracking_id(db, tracking_id)

            if user:
                # Reverse the old amount effect first
                prev_total_payable = user.total_payable or 0
                prev_total_payment = user.total_payment or 0

                new_total_payable = prev_total_payable - old_amount + new_amount
                new_total_due = max(0, new_total_payable - prev_total_payment)
                new_available_amount = max(0, prev_total_payment - new_total_payable)

                # Prepare update schema
                payment_info = PayableInfoUpdateSchema(
                    total_payable=new_total_payable,
                    total_available_amount=new_available_amount,
                    total_due=new_total_due,
                    group_leader_code=group_leader_code if group_leader_code else None,
                    tracking_id=tracking_id if tracking_id else None
                )

                # Update payment info (for either leader or pilgrim)
                await pilgrim_payment_repository.update_payment_info(db, payment_info)

    updated_payment = await payment_repository.update_payable(db, payable_id, filtered_data)
    return updated_payment
