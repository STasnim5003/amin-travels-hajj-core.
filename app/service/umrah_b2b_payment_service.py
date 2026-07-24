from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import num_to_words
from app.core.utils.get_current_time import get_current_time
from data.model.umrah_requisition_model import UmrahRequisitionModel
from data.repository import umrah_b2b_payment_repository, umrah_b2b_agent_repository, umrah_requisition_repository
from infrastructure.schema.umrah_b2b_payment_schema import (
    UmrahB2BPaymentCreate,
    UmrahB2BPaymentResponse,
    UmrahB2BPaymentUpdate, UmrahB2BBillingInvoiceBuildSchema,
    UmrahB2BTransactionList
)
import json


async def create_umrah_b2b_payment(db: AsyncSession, request: UmrahB2BPaymentCreate, agency_name: str, username: str):
    try:

        if request.amount <= 0:
            raise HTTPException(status_code=400, detail='Amount must be positive')

        b2b_agent = await umrah_b2b_agent_repository.get_umrah_b2b_agent_by_name(db=db,
                                                                                 b2b_agent_name=request.b2b_agent_name,
                                                                                 agency_name=agency_name)

        if not b2b_agent:
            raise HTTPException(status_code=400, detail='B2B Agent does not exist')

        request_dict = request.model_dump(exclude_none=True)
        request_dict['agency_name'] = agency_name
        request_dict['created_by'] = username
        request_dict['updated_by'] = username

        result = await umrah_b2b_payment_repository.create_umrah_b2b_payment(db=db, request_dict=request_dict)
        return UmrahB2BPaymentResponse.model_validate(result)
    except Exception as e:
        raise e


async def get_umrah_b2b_payments(
        db: AsyncSession,
        agency_name: str,
):
    try:
        result = await umrah_b2b_payment_repository.get_umrah_b2b_payments(
            db=db,
            agency_name=agency_name,
        )

        if not result:
            return []

        response = []

        for agent in result:
            requisitions = []
            payments = []

            for item in agent["payments"]:
                if item["office_code"] is not None:
                    item["type"] = "Requisition"
                    requisitions.append(item)
                else:
                    item["type"] = "Payments"
                    item["invoice_no"] = None
                    payments.append(item)

            response.append({
                "b2b_agent_name": agent["b2b_agent_name"],
                "total_bill": agent["total_bill"],
                "total_credit": agent["total_credit"],
                "due": agent["due"],
                "available_balance": agent["available_balance"],
                "payments": requisitions + payments
            })

        return response

    except Exception as e:
        raise e


async def get_umrah_b2b_payment_by_id(db: AsyncSession, agency_name: str, payment_id: int):
    result = await umrah_b2b_payment_repository.get_umrah_b2b_payment_by_id(db, payment_id)

    if not result:
        raise HTTPException(status_code=400, detail="Payment not found")

    if result.agency_name != agency_name:
        raise HTTPException(status_code=400, detail="Agency mismatch")

    return UmrahB2BPaymentResponse.model_validate(result)


async def update_umrah_b2b_payment(db: AsyncSession, request: UmrahB2BPaymentUpdate, agency_name: str, username: str):
    try:
        result = await umrah_b2b_payment_repository.get_umrah_b2b_payment_by_id(db, request.id)

        if not result:
            raise HTTPException(status_code=400, detail="Payment not found")

        if result.agency_name != agency_name:
            raise HTTPException(status_code=400, detail="Agency mismatch")

        request_dict = request.model_dump(exclude_none=True)
        request_dict["updated_by"] = username
        request_dict["updated_at"] = get_current_time()

        b2b_agent_name = result.b2b_agent_name

        if b2b_agent_name != request_dict.get("b2b_agent_name"):
            raise HTTPException(status_code=400, detail="B2B Agent name cannot be changed")

        b2b_agent = await umrah_b2b_agent_repository.get_umrah_b2b_agent_by_name(db=db, b2b_agent_name=b2b_agent_name,
                                                                                 agency_name=agency_name)

        current_credit = b2b_agent.total_credit - result.amount + request_dict["amount"]
        current_due = max(b2b_agent.total_bill - current_credit, 0)

        b2b_finance_update = {
            'total_credit': current_credit,
            'total_due': current_due,
            'agency_name': agency_name,
        }
        result = await umrah_b2b_payment_repository.update_umrah_b2b_payment(db, request_dict, b2b_finance_update)

        return UmrahB2BPaymentResponse.model_validate(result)
    except Exception as e:
        raise e


async def delete_umrah_b2b_payment(db: AsyncSession, agency_name: str, payment_id: int, username: str):
    result = await umrah_b2b_payment_repository.get_umrah_b2b_payment_by_id(db, payment_id)

    if not result:
        raise HTTPException(status_code=400, detail="Payment not found")

    if result.agency_name != agency_name:
        raise HTTPException(status_code=400, detail="Agency mismatch")

    b2b_agent_name = result.b2b_agent_name
    b2b_agent = await umrah_b2b_agent_repository.get_umrah_b2b_agent_by_name(db=db, b2b_agent_name=b2b_agent_name,
                                                                             agency_name=agency_name)

    current_credit = b2b_agent.total_credit - result.amount
    current_due = max(0, b2b_agent.total_bill - current_credit)

    b2b_finance_update = {
        'total_credit': current_credit,
        'total_due': max(0, current_due),
        'name': b2b_agent_name,
        'agency_name': agency_name
    }

    return await umrah_b2b_payment_repository.delete_umrah_b2b_payment(db, payment_id, b2b_finance_update)


async def get_umrah_invoice_payments_for_b2b_agent(db: AsyncSession, agency_name: str, b2b_agent_name: str):
    try:
        row = await umrah_b2b_payment_repository.get_umrah_payments_for_b2b_agent(db=db, agency_name=agency_name,
                                                                                  b2b_agent_name=b2b_agent_name)
        if not row:
            return None

        return UmrahB2BTransactionList.model_validate(row)
    except Exception as e:
        raise e


async def get_umrah_b2b_billing_invoice(
    db: AsyncSession,
    agency_name: str,
    amin_office_code: str,
):
    try:
        invoice_data = await umrah_b2b_payment_repository.get_umrah_b2b_billing_invoice(
            db=db,
            amin_office_code=amin_office_code,
        )

        if not invoice_data:
            raise HTTPException(
                status_code=400,
                detail="Requisition doesn't exist",
            )

        requisition, invoice_no = invoice_data

        if requisition.agency_name != agency_name:
            raise HTTPException(
                status_code=400,
                detail="Agency name does not match",
            )

        data = {
            c.name: getattr(requisition, c.name)
            for c in UmrahRequisitionModel.__table__.columns
        }

        data["invoice_no"] = invoice_no
        data["total_price_in_words"] = num_to_words.amount_to_words(
            data.get("total_price") or 0
        )

        return data

    except Exception as e:
        raise e