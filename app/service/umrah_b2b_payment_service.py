from datetime import date

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import num_to_words
from app.core.utils.get_current_time import get_current_time
from data.repository import umrah_b2b_payment_repository, umrah_b2b_agent_repository, umrah_requisition_repository
from infrastructure.schema.umrah_b2b_payment_schema import (
    UmrahB2BPaymentCreate,
    UmrahB2BPaymentResponse,
    UmrahB2BPaymentListResponse,
    UmrahB2BPaymentUpdate, B2BPaymentItem, B2BAgentPaymentResponse, UmrahB2BBillingInvoiceBuildSchema
)


async def create_umrah_b2b_payment(db: AsyncSession, request: UmrahB2BPaymentCreate, agency_name: str, username: str):
    try:

        if request.amount <= 0:
            raise HTTPException(status_code=400, detail='Amount must be positive')

        umrah_requisition = await umrah_requisition_repository.get_requisition_by_office_code(db=db,
                                                                                              office_code=request.amin_office_code)

        if not umrah_requisition:
            raise HTTPException(status_code=400, detail='Requisition does not exist')

        request_dict = request.model_dump(exclude_none=True)
        request_dict['agency_name'] = agency_name
        request_dict['created_by'] = username
        request_dict['updated_by'] = username

        discount = umrah_requisition.discount or 0

        total_payment = umrah_requisition.total_payment + request.amount
        requisition_price_update_dict = {
            'total_payment': total_payment,
            'total_due': max(0, umrah_requisition.total_price - (total_payment + discount)),
        }

        result = await umrah_b2b_payment_repository.create_umrah_b2b_payment(db=db, request_dict=request_dict,
                                                                                       requisition_price_update_dict=requisition_price_update_dict)
        return UmrahB2BPaymentResponse.model_validate(result)
    except Exception as e:
        raise e


async def get_umrah_b2b_payments(db: AsyncSession, agency_name: str):
    try:
        results = await umrah_b2b_payment_repository.get_umrah_b2b_payments(db, agency_name)

        return [UmrahB2BPaymentListResponse(**row) for row in results]
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

        requisition = await umrah_requisition_repository.get_requisition_by_office_code(db=db, office_code=request_dict['amin_office_code'])

        current_payment = requisition.total_payment - result.amount + request_dict["amount"]
        current_due = requisition.total_price - requisition.discount - current_payment

        requisition_update_dict = {
            'total_payment': current_payment,
            'total_due': max(0, current_due),
        }
        result = await umrah_b2b_payment_repository.update_umrah_b2b_payment(db, request_dict, requisition_update_dict)

        return UmrahB2BPaymentResponse.model_validate(result)
    except Exception as e:
        raise e


async def delete_umrah_b2b_payment(db: AsyncSession, agency_name: str, payment_id: int, username: str):
    result = await umrah_b2b_payment_repository.get_umrah_b2b_payment_by_id(db, payment_id)

    if not result:
        raise HTTPException(status_code=400, detail="Payment not found")

    if result.agency_name != agency_name:
        raise HTTPException(status_code=400, detail="Agency mismatch")

    requisition = await umrah_requisition_repository.get_requisition_by_office_code(db=db, office_code=result.amin_office_code)

    current_payment = requisition.total_payment - result.amount
    current_due = requisition.total_price - requisition.discount - current_payment

    requisition_update_dict = {
        'total_payment': current_payment,
        'total_due': max(0, current_due),
        'amin_office_code' : result.amin_office_code
    }

    return await umrah_b2b_payment_repository.delete_umrah_b2b_payment(db, payment_id, requisition_update_dict)


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


async def get_umrah_b2b_billing_invoice(db:AsyncSession, agency_name:str, amin_office_code:str):
    try:
        invoice_data = await umrah_b2b_payment_repository.get_umrah_b2b_billing_invoice(db=db, amin_office_code=amin_office_code)
        if not invoice_data:
            raise HTTPException(status_code=400, detail="Requisition Doesn't Exists")

        if invoice_data['agency_name'] != agency_name:
            raise HTTPException(status_code=400, detail='Agency name does not match')

        return UmrahB2BBillingInvoiceBuildSchema(
            amin_office_code=amin_office_code,
            b2b_agent_name=invoice_data.get('b2b_agent_name'),
            sales_person=invoice_data.get('sales_person'),
            name=invoice_data.get('name'),
            mobile_no=invoice_data.get('mobile_no'),
            total_price=invoice_data.get('total_price'),
            total_due=invoice_data.get('total_due'),
            total_payment=invoice_data.get('total_payment'),
            discount=invoice_data.get("discount"),
            no_of_adults=invoice_data.get('adult_traveller'),
            no_of_children=invoice_data.get('other_traveller').get('child') if invoice_data.get(
                'other_traveller') else None,
            no_of_infants=invoice_data.get('other_traveller').get('infant') if invoice_data.get(
                'other_traveller') else None,
            per_head_price_adult=invoice_data.get('per_head_price_adult'),
            per_head_price_children=invoice_data.get('per_head_price_child'),
            per_head_price_infants=invoice_data.get('per_head_price_infant'),
            agency_name=invoice_data.get('agency_name'),
            total_price_in_words=num_to_words.amount_to_words(invoice_data.get('total_price')),
            total_due_in_words=num_to_words.amount_to_words(invoice_data.get('total_due')),
            total_payment_in_words=num_to_words.amount_to_words(invoice_data.get('total_payment'))
        )
    except Exception as e:
        raise e