import random
import random
import string
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import num_to_words
from data.repository import payment_repository, admin_user_repository, pilgrim_repository, file_repository
from infrastructure.schema.payment_schema import PaginatedPaymentResponseForGroupLeader, \
    PayableInfoUpdateSchema, \
    GroupLeaderPayableBaseSchema, GroupLeaderPaymentBaseSchema, OverallSummarySchema, \
    BankSummarySchema, PaginatedPaymentResponseForAgency, ReceiptPrintSchema, PayableUpdateSchema


async def create_payable_for_group_leader(db: AsyncSession, payment_request: GroupLeaderPayableBaseSchema,
                                          agency_name: str):
    if payment_request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount should be positive")

    # check group leader
    try:
        existing_group_leader = await admin_user_repository.get_admin_user_by_code(db, payment_request.group_leader)
        if not existing_group_leader:
            raise HTTPException(status_code=400, detail="Group leader does not exist")

    except Exception as e:
        raise e

    # Generate an 8-character random alphanumeric transaction ID
    transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    payment_data = payment_request.model_dump(exclude_unset=True)
    payment_data.update({
        "transaction_id": transaction_id,
        "created_by": agency_name,
        "updated_by": agency_name,
        "no_of_hajji": len(payment_request.pilgrims_tracking_id)
    })

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

    try:
        # if existing_group_leader.is_payment_distributed and len(payment_request.pilgrims_tracking_id) > 0:
        #     result = await payment_repository_multiple_pilgrims.create_payable_for_multiple_pilgrims(db, payment_data,
        #                                                                                              agency_name,
        #                                                                                              payable_info)
        #     return result
        # else:
        #     result = await payment_repository.create_payable_for_group_leader(db, payment_data, payable_info,
        #                                                                       agency_name)
        #     return result
        result = await payment_repository.create_payable_for_group_leader(db, payment_data, payable_info,
                                                                          agency_name)
        return result
    except Exception as e:
        raise e


async def create_group_leader_payment(db: AsyncSession, request: GroupLeaderPaymentBaseSchema, agency_name: str,
                                      receipt: UploadFile):
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount should be positive")

    try:
        # Check Group Leader & Agency
        existing_group_leader = await admin_user_repository.get_admin_user_by_code(db, request.group_leader)
        if not existing_group_leader or existing_group_leader.agency_name != agency_name:
            raise HTTPException(status_code=400, detail="Group leader does not exist")
    except Exception as e:
        raise e

    receipt_data = []
    if receipt:
        try:
            receipt_resp = await file_repository.upload_file(file=receipt, name="receipt")
            receipt_data.append(receipt_resp.model_dump())
        except Exception as e:
            raise e

    transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    payment_data = request.model_dump(exclude_unset=True)
    payment_data.update({
        "transaction_id": transaction_id,
        "created_by": agency_name,
        "updated_by": agency_name,
        "no_of_hajji": len(request.pilgrims_tracking_id),
        "receipt": receipt_data
    })

    prev_total_payable = existing_group_leader.total_payable or 0
    new_total_payment = (existing_group_leader.total_payment or 0) + request.amount

    new_total_available = max(0, new_total_payment - prev_total_payable)
    new_total_due = max(0, prev_total_payable - new_total_payment)

    payment_info = PayableInfoUpdateSchema(
        total_payment=new_total_payment,
        total_available_amount=new_total_available,
        total_due=new_total_due,
        group_leader_code=request.group_leader
    )
    try:
        # if existing_group_leader.is_payment_distributed and len(request.pilgrims_tracking_id) > 0:
        #     result = await payment_repository_multiple_pilgrims.create_payment_for_multiple_pilgrims(db, payment_data,
        #                                                                                              agency_name,
        #                                                                                              payment_info)
        #     return result
        # else:
        #     result = await payment_repository.create_payment_for_group_leader(db, payment_data, agency_name,
        #                                                                       payment_info)
        #
        #     return result
        result = await payment_repository.create_payment_for_group_leader(db, payment_data, agency_name,
                                                                          payment_info)

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
        grouped_payments=payments,
        page=page,
        size=size,
        total=total,
        total_payable=group_leader_total_payable,
        total_payment=group_leader_total_payment,
        total_due=group_leader_total_due,
        total_available_amount=group_leader_total_available_amount
    )


async def get_agency_payments(
        user_type,
        db,
        agency_name: str,
        group_leader: str | None,
        tracking_id: str | None,
        page: int,
        size: int
):
    try:
        result = await payment_repository.get_payment_summary_for_agency(
            user_type, db, agency_name, page, size, group_leader, tracking_id
        )

        # Extract data from result
        grouped_payments = result.get("grouped_payments", {}) or {}
        total = result.get("total_count", 0)  # Get actual total count
        bank_summary_data = result.get("bank_summary", [])
        overall_summary_data = result.get("overall_summary", {})

        # Map bank summary data to schema
        bank_summary = []
        for bank in bank_summary_data:
            bank_summary.append(
                BankSummarySchema(
                    bank_info_id=bank.get("bank_info_id"),
                    bank_name=bank.get("bank_name"),
                    bank_branch=bank.get("bank_branch"),
                    bank_account=bank.get("bank_account"),
                    total_payment=bank.get("total_payment"),
                )
            )

        # Map overall summary data to schema
        overall_summary = OverallSummarySchema(
            total_payment=overall_summary_data.get("total_payment"),
            last_7_days_payment=overall_summary_data.get("last_7_days_payment"),
            today_payment=overall_summary_data.get("today_payment"),
            yesterday_payment=overall_summary_data.get("yesterday_payment"),
        )

        payment_fields = set()
        for payments in grouped_payments.values():
            if payments and isinstance(payments, list):
                for payment in payments:
                    payment_fields.update(payment.keys())

        final_result = []
        for key, payments in grouped_payments.items():
            if not payments:
                continue

            name = payments[0].get("username")
            mobile_no = payments[0].get("mobile_no")

            base_fields = {field: None for field in payment_fields}
            base_fields.update({
                "name": key,
                "username": name,
                "mobile_no": mobile_no,
                "children": payments
            })

            final_result.append(base_fields)

        # Return paginated response
        return PaginatedPaymentResponseForAgency(
            page=page,
            size=size,
            total=total,
            bank_summary=bank_summary,
            overall_summary=overall_summary,
            grouped_payments=final_result
        )


    except Exception as e:
        raise e


async def update_payable(
        db: AsyncSession,
        payable_data: PayableUpdateSchema,
        agency_name: str
):
    if payable_data.amount and payable_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")

    existing_payment = await payment_repository.get_by_id(db, payable_data.payable_id)

    if existing_payment.created_by != agency_name:
        raise HTTPException(status_code=403, detail="Unauthorized to update this payable")

    if existing_payment.tracking_id and existing_payment.tracking_id != payable_data.tracking_id:
        raise HTTPException(status_code=400, detail="Tracking ID does not match")

    if existing_payment.group_leader and existing_payment.group_leader != payable_data.group_leader:
        raise HTTPException(status_code=400, detail="Group Leader does not match")

    updated_time_bd = datetime.now(ZoneInfo("Asia/Dhaka"))
    updated_time_bd = updated_time_bd.replace(tzinfo=None)

    payable_data_dict = payable_data.model_dump(exclude_none=True)
    payable_data_dict['updated_by'] = agency_name
    payable_data_dict['updated_at'] = updated_time_bd

    finance_info = {}

    if payable_data.amount and existing_payment.amount != payable_data.amount and existing_payment.tracking_id:
        pilgrim = await pilgrim_repository.get_pilgrim_by_tracking_id(db, existing_payment.tracking_id)

        curr_payable = pilgrim.total_payable
        curr_payment = pilgrim.total_payment
        package_price_discount = pilgrim.package_price_discount


        total_payable = curr_payable - existing_payment.amount + payable_data.amount
        total_due = max(0, total_payable - curr_payment)
        total_available_amount = max(0, curr_payment - total_payable)
        actual_payable = total_payable - package_price_discount

        finance_info = {
            'total_payable': total_payable,
            'total_available_amount': total_available_amount,
            'total_due': total_due,
            'actual_payable': actual_payable,
            'tracking_id': pilgrim.tracking_id,
        }

    updated_payment = await payment_repository.update_payable(db, payable_data_dict, finance_info)
    return updated_payment


async def get_payment_by_id(db: AsyncSession, payment_id: int):
    try:
        result = await payment_repository.get_payment_by_id(db, payment_id)
        payment = result["payment"]
        bank_info = result.get("bank_info")

        # Optional: fetch group leader or pilgrim name
        group_leader_name = None
        payer_name = None
        payee_name = payment.created_by

        if payment.group_leader:
            admin_user = await admin_user_repository.get_admin_user_by_code(db, payment.group_leader)
            group_leader_name = admin_user.name if admin_user else None
            payer_name = group_leader_name
        elif payment.tracking_id:
            pilgrim = await pilgrim_repository.get_pilgrim_by_tracking_id(db, payment.tracking_id)
            payer_name = pilgrim.name_en if pilgrim else None

        amount_to_words = num_to_words.amount_to_words(payment.amount)

        receipt = ReceiptPrintSchema(
            id=payment.id,
            description=getattr(payment, "description", None),
            date=getattr(payment, "date", None),
            amount=payment.amount,
            group_leader=payment.group_leader,
            payer_name=payer_name,
            payee_name=payee_name,
            category=payment.category,
            transaction_id=getattr(payment, "transaction_id", None),
            tracking_id=payment.tracking_id,
            payment_category=getattr(payment, "payment_category", None),
            way_of_payment=getattr(payment, "way_of_payment", None),
            bank_info_id=payment.bank_info_id,
            bank_name=bank_info.name if bank_info else None,
            bank_branch=bank_info.branch if bank_info else None,
            bank_account_no=bank_info.account_no if bank_info else None,
            amount_in_words=amount_to_words,
            cheque_no=payment.cheque_no,
            cheque_bank=payment.cheque_bank,
            voucher_no=payment.voucher_no
        )

        return receipt

    except Exception as e:
        raise e
