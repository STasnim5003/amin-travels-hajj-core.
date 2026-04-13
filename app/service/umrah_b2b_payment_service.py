from datetime import date

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from data.repository import umrah_b2b_payment_repository, umrah_b2b_agent_repository
from infrastructure.schema.umrah_b2b_payment_schema import (
    UmrahB2BPaymentCreate,
    UmrahB2BPaymentResponse,
    UmrahB2BPaymentListResponse,
    UmrahB2BPaymentUpdate, B2BPaymentItem, B2BAgentPaymentResponse
)


async def create_umrah_b2b_payment(db: AsyncSession, request: UmrahB2BPaymentCreate, agency_name: str, username: str):
    try:
        if request.bill <= 0 or request.credit <= 0:
            raise HTTPException(status_code=400, detail="Amount Must Be Greater than 0")
        request_dict = request.model_dump(exclude_none=True)
        request_dict["agency_name"] = agency_name
        request_dict["created_by"] = username
        request_dict["updated_by"] = username

        result = await umrah_b2b_payment_repository.create_umrah_b2b_payment(db, request_dict)
        return UmrahB2BPaymentResponse.model_validate(result)
    except Exception as e:
        raise e


async def get_umrah_b2b_payments(db: AsyncSession, agency_name: str):
    try:
        results = await umrah_b2b_payment_repository.get_umrah_b2b_payments(db, agency_name)

        return UmrahB2BPaymentListResponse(
            payment_list=[UmrahB2BPaymentResponse.model_validate(r) for r in results]
        )
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

        b2b_agent_finance = await umrah_b2b_agent_repository.get_umrah_b2b_agent_by_name(db=db,
                                                                                         b2b_agent_name=result.b2b_agent_name,
                                                                                         agency_name=agency_name)
        total_bill = b2b_agent_finance.total_bill - result.bill + request_dict["bill"]
        total_credit = b2b_agent_finance.total_credit - result.credit + request_dict["credit"]
        total_due = max(0, total_bill - total_credit)

        b2b_agent_finance_update_dict = {
            'total_bill': total_bill,
            'total_credit': total_credit,
            'total_due': total_due,
            'b2b_agent_name': result.b2b_agent_name,
            'updated_by': username,
            'updated_at': get_current_time()
        }
        result = await umrah_b2b_payment_repository.update_umrah_b2b_payment(db, request_dict,
                                                                             b2b_agent_finance_update_dict)

        return UmrahB2BPaymentResponse.model_validate(result)
    except Exception as e:
        raise e


async def delete_umrah_b2b_payment(db: AsyncSession, agency_name: str, payment_id: int, username: str):
    result = await umrah_b2b_payment_repository.get_umrah_b2b_payment_by_id(db, payment_id)

    if not result:
        raise HTTPException(status_code=400, detail="Payment not found")

    if result.agency_name != agency_name:
        raise HTTPException(status_code=400, detail="Agency mismatch")

    b2b_agent_finance = await umrah_b2b_agent_repository.get_umrah_b2b_agent_by_name(db=db,
                                                                                     b2b_agent_name=result.b2b_agent_name,
                                                                                     agency_name=agency_name)
    total_bill = b2b_agent_finance.total_bill - result.bill
    total_credit = b2b_agent_finance.total_credit - result.credit
    total_due = max(0, total_bill - total_credit)

    b2b_agent_finance_update_dict = {
        'total_bill': total_bill,
        'total_credit': total_credit,
        'total_due': total_due,
        'b2b_agent_name': result.b2b_agent_name,
        'updated_by': username,
        'updated_at': get_current_time()
    }

    return await umrah_b2b_payment_repository.delete_umrah_b2b_payment(db, payment_id, b2b_agent_finance_update_dict)


async def get_umrah_payments_for_b2b_agent(db: AsyncSession, agency_name: str, b2b_agent_name: str):
    try:
        row = await umrah_b2b_payment_repository.get_umrah_payments_for_b2b_agent(db=db, agency_name=agency_name,
                                                                                  b2b_agent_name=b2b_agent_name)
        if not row:
            return None

        payment_list = []
        if row.payment_list:
            payment_list = [
                B2BPaymentItem(**payment)
                for payment in row.payment_list
            ]

        return B2BAgentPaymentResponse(
            name=row.name,
            agency_name=row.agency_name,
            total_bill=row.total_bill,
            total_credit=row.total_credit,
            total_due=row.total_due,
            payment_list=payment_list
        )
    except Exception as e:
        raise e
