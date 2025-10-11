from typing import List, Optional

from fastapi import UploadFile, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.admin_user_model import AdminUserModel
from data.repository import payment_repository, file_repository, pilgrim_repository, pilgrim_payment_repository
from infrastructure.schema.payment_schema import PaymentSchema, PaymentResponseSchema, \
    PaginatedPaymentResponseForGroupLeader, PaginatedPaymentResponseForAgency, AgencyPaymentSchemaForGroupLeader, \
    PayableInfoUpdateSchema


async def create_payable_for_group_leader(db: AsyncSession, payment_request: PaymentSchema, agency_name: str,
                                          receipt: Optional[List[UploadFile]]):
    receipt_data = []
    if receipt:
        try:
            for file in receipt:
                receipt_resp = await file_repository.upload_file(file=file, name="receipt")
                receipt_data.append(receipt_resp.model_dump())
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"File upload failed: {str(e)}")
    try:
        return await payment_repository.create_payable_for_group_leader(db, payment_request, agency_name, receipt_data)
    except Exception as e:
        raise e


async def create_group_leader_payment(db: AsyncSession, request: AgencyPaymentSchemaForGroupLeader, agency_name: str,
                                      receipt: List[UploadFile] = None):
    receipt_data = []
    if receipt:
        try:
            for file in receipt:
                receipt_resp = await file_repository.upload_file(file=file, name="receipt")
                receipt_data.append(receipt_resp.model_dump())
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"File upload failed: {str(e)}")

    try:
        return await payment_repository.create_payment_for_group_leader(db, request, agency_name, receipt_data)
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
        total_payable=group_leader_total_payable,
        total_payment=group_leader_total_payment,
        total_due=group_leader_total_due,
        total_available_amount=group_leader_total_available_amount
    )


async def get_agency_payments(
        db,
        agency_name: str,
        group_leader: str | None,
        category: str | None,
        page: int,
        size: int
):
    (
        payments,
        total
    ) = await payment_repository.get_payments_by_agency(db, agency_name, group_leader, category, page, size)

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

    return PaginatedPaymentResponseForAgency(
        payments=payables,
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



