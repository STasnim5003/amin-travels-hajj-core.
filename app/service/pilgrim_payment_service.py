import random
import string
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import num_to_words
from data.repository import pilgrim_payment_repository, pilgrim_repository, file_repository, payment_repository, \
    admin_user_repository
from infrastructure.schema.payment_schema import PayableInfoUpdateSchema, PaymentResponseSchema, \
    PaginatedPaymentResponseForGroupLeader, PilgrimPayableBaseSchema, PilgrimPaymentBaseSchema, \
    PilgrimPayableReportSchema, GroupLeaderPayableReportSchema, PaymentUpdateSchema


async def create_payable_for_pilgrim(
        db: AsyncSession, payment_data: PilgrimPayableBaseSchema, agency_name: str
) -> PaymentResponseSchema:
    if payment_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    try:
        pilgrim = await pilgrim_repository.get_pilgrim_by_tracking_id(db, payment_data.tracking_id)
        if not pilgrim or pilgrim.group_name != agency_name:
            raise HTTPException(status_code=400, detail="Pilgrim with tracking id not found")

    except Exception as e:
        raise e

    # Update Pilgrim TK Info
    pilgrim_prev_total_payable = pilgrim.total_payable or 0
    pilgrim_prev_total_payment = pilgrim.total_payment or 0
    prev_actual_payable = pilgrim.actual_payable or 0

    new_total_payable = pilgrim_prev_total_payable + payment_data.amount
    new_total_due = max(0, new_total_payable - pilgrim_prev_total_payment)
    new_total_available_amount = max(0, pilgrim_prev_total_payment - new_total_payable)
    new_actual_payable = prev_actual_payable + payment_data.amount

    payable_info = PayableInfoUpdateSchema(
        tracking_id=payment_data.tracking_id,
        total_payable=new_total_payable,
        total_due=new_total_due,
        total_available_amount=new_total_available_amount,
        actual_payable=new_actual_payable
    )

    # Create Payable Info
    transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    payment_request_dict = payment_data.model_dump(exclude_unset=True)
    payment_request_dict.update({
        "transaction_id": transaction_id,
        "created_by": agency_name,
        "updated_by": agency_name
    })

    try:
        result = await pilgrim_payment_repository.create_payable_for_pilgrim(db, payment_request_dict, payable_info)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def create_payment_for_pilgrim(
        db: AsyncSession, payment_data: PilgrimPaymentBaseSchema, agency_name: str, receipt: UploadFile
):
    if payment_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    try:
        pilgrim = await pilgrim_repository.get_pilgrim_by_tracking_id(db, payment_data.tracking_id)
        if not pilgrim or pilgrim.group_name != agency_name:
            raise HTTPException(status_code=400, detail="Pilgrim with tracking id not found")

    except Exception as e:
        raise e

    receipt_data = []
    if receipt:
        try:
            receipt_resp = await file_repository.upload_file(file=receipt, name="receipt")
            receipt_data.append(receipt_resp.model_dump())
        except Exception as e:
            raise e

    prev_total_payable = pilgrim.total_payable or 0
    prev_total_payment = pilgrim.total_payment or 0

    new_total_payment = prev_total_payment + payment_data.amount
    new_total_due = max(0, prev_total_payable - new_total_payment)
    new_available_amount = max(0, new_total_payment - prev_total_payable)

    payment_info = PayableInfoUpdateSchema(
        total_payment=new_total_payment,
        total_available_amount=new_available_amount,
        total_due=new_total_due,
        tracking_id=payment_data.tracking_id
    )

    transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    payment_request_dict = payment_data.model_dump(exclude_unset=True)
    payment_request_dict.update({
        "transaction_id": transaction_id,
        "created_by": agency_name,
        "updated_by": agency_name,
        "receipt": receipt_data
    })

    try:
        result = await pilgrim_payment_repository.create_payment_for_pilgrim(db, payment_request_dict, payment_info)
        return PaymentResponseSchema.model_validate(result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def get_pilgrim_payments(
        db,
        tracking_id: str,
        category: str | None,
        page: int,
        size: int
):
    (
        payments,
        total,
        pilgrim_total_payable,
        pilgrim_total_payment,
        pilgrim_total_due,
        pilgrim_total_available_amount
    ) = await pilgrim_payment_repository.get_payments_by_tracking_id(db, tracking_id, page, size)

    return PaginatedPaymentResponseForGroupLeader(
        grouped_payments=payments,
        page=page,
        size=size,
        total=total,
        total_payable=pilgrim_total_payable,
        total_payment=pilgrim_total_payment,
        total_due=pilgrim_total_due,
        total_available_amount=pilgrim_total_available_amount
    )


async def get_pilgrim_payable_report(db: AsyncSession, payable, agency_name: str):
    try:

        pilgrim = await pilgrim_repository.get_pilgrim_by_tracking_id(db, payable.tracking_id)
        if not pilgrim:
            raise HTTPException(status_code=400, detail="Pilgrim not found")

        if payable.created_by != agency_name or pilgrim.group_name != agency_name:
            raise HTTPException(status_code=400, detail="Payable not belong to this agency")

        amount_in_words = num_to_words.amount_to_words(payable.amount)
        return PilgrimPayableReportSchema(
            id=payable.id,
            name_en=pilgrim.name_en,
            name_bn=pilgrim.name_bn,
            nid=pilgrim.nid,
            date_of_birth=pilgrim.date_of_birth,
            gender=pilgrim.gender,
            description=payable.description,
            date=payable.date,
            amount=payable.amount,
            tracking_id=payable.tracking_id,
            amount_in_words=amount_in_words,
            package_name=pilgrim.package_name,
            package_duration=pilgrim.package_duration,
            package_bed_types=pilgrim.package_bed_types,
            add_ons_services=pilgrim.add_ons_services,
            agency_name=agency_name
        )

    except Exception as e:
        raise e


async def get_group_leader_payable_report_data(db: AsyncSession, payable, agency_name: str):
    try:
        group_leader = await admin_user_repository.get_admin_user_by_code(db, payable.group_leader)
        if not group_leader:
            raise HTTPException(status_code=400, detail="Group leader not found")
        if payable.created_by != agency_name or group_leader.agency_name != agency_name:
            raise HTTPException(status_code=400, detail="Payable not belong to this group leader")

        response = await pilgrim_payment_repository.get_group_leader_payable_report_data(db=db, group_leader=payable.group_leader)

        package_wise_haji_summary = []

        for row in response:
            package_wise_haji_summary.append({
                "package_name": row.package_name,
                "package_duration": row.package_duration,
                "package_bed_types": row.package_bed_types,
                "total_haji": row.total_haji,
                "total_actual_payable": row.total_actual_payable,
            })

        amount_in_words = num_to_words.amount_to_words(payable.amount)

        return GroupLeaderPayableReportSchema(
            id=payable.id,
            name_en=group_leader.name,
            code=group_leader.code,
            agency_name=group_leader.agency_name,
            amount = payable.amount,
            amount_in_words=amount_in_words,
            summary=package_wise_haji_summary
        )
    except Exception as e:
        raise e


async def get_payable_report_data(db:AsyncSession, payable_id:int, agency_name:str):
    try:
        payable = await payment_repository.get_by_id(db, payable_id)
        if not payable:
            raise HTTPException(status_code=400, detail="Payable not found")

        if payable.tracking_id:
            return await get_pilgrim_payable_report(db, payable, agency_name)
        else:
            return await get_group_leader_payable_report_data(db, payable, agency_name)
    except Exception as e:
        raise e


async def get_payable_by_id(db:AsyncSession, payable_id:int, agency_name:str):
    try:
        payable = await payment_repository.get_by_id(db, payable_id)

        if payable.created_by != agency_name:
            raise HTTPException(status_code=400, detail="Payable not belong to this agency")
        return payable
    except Exception as e:
        raise e


async def update_payment(db:AsyncSession, payment_update_schema:PaymentUpdateSchema, agency_name:str, receipt:Optional[UploadFile]):
    try:
        if payment_update_schema.amount is not None and payment_update_schema.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than zero")

        existing_payment = await payment_repository.get_by_id(db, payment_update_schema.payment_id)

        if existing_payment.category != "Payment":
            raise HTTPException(status_code=400, detail="It is not Payment")

        if existing_payment.created_by != agency_name:
            raise HTTPException(status_code=403, detail="Unauthorized to update this payable")

        if existing_payment.tracking_id and existing_payment.tracking_id != payment_update_schema.tracking_id:
            raise HTTPException(status_code=400, detail="Tracking ID does not match")

        if existing_payment.group_leader and existing_payment.group_leader != payment_update_schema.group_leader:
            raise HTTPException(status_code=400, detail="Group Leader does not match")


        updated_time_bd = datetime.now(ZoneInfo("Asia/Dhaka"))
        updated_time_bd = updated_time_bd.replace(tzinfo=None)

        payment_data_dict = payment_update_schema.model_dump(exclude_none=True)
        payment_data_dict['updated_by'] = agency_name
        payment_data_dict['updated_at'] = updated_time_bd

        receipt_data = []
        if receipt:
            try:
                receipt_resp = await file_repository.upload_file(file=receipt, name="receipt")
                receipt_data.append(receipt_resp.model_dump())
                payment_data_dict['receipt'] = receipt_data
            except Exception as e:
                raise e

        finance_info = {}

        # pilgrim finance info
        if payment_update_schema.amount and existing_payment.amount != payment_update_schema.amount and existing_payment.tracking_id:
            pilgrim = await pilgrim_repository.get_pilgrim_by_tracking_id(db, existing_payment.tracking_id)

            curr_payable = pilgrim.total_payable
            curr_payment = pilgrim.total_payment

            total_payment = curr_payment - existing_payment.amount + payment_update_schema.amount
            total_due = max(0, curr_payable - total_payment)
            total_available_amount = max(0, total_payment - curr_payable)

            finance_info = {
                'total_payment': total_payment,
                'total_available_amount': total_available_amount,
                'total_due': total_due,
                'tracking_id': pilgrim.tracking_id,
                'updated_by' : agency_name,
                'updated_at' : updated_time_bd
            }

        # group leader finance info
        elif payment_update_schema.amount and existing_payment.amount != payment_update_schema.amount and existing_payment.group_leader:
            group_leader = await admin_user_repository.get_admin_user_by_code(db, existing_payment.group_leader)

            curr_payable = group_leader.total_payable
            curr_payment = group_leader.total_payment

            total_payment = curr_payment - existing_payment.amount + payment_update_schema.amount
            total_due = max(0, curr_payable - total_payment)
            total_available_amount = max(0, total_payment - curr_payable)

            finance_info = {
                'total_payment': total_payment,
                'total_available_amount': total_available_amount,
                'total_due': total_due,
                'code': existing_payment.group_leader,
                'updated_by': agency_name,
                'updated_at': updated_time_bd
            }

        updated_payment = await payment_repository.update_payable_payment(db, payment_data_dict, finance_info)
        return updated_payment
    except Exception as e:
        raise e
