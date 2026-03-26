from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from data.repository import umrah_customer_billing_repository, umrah_requisition_repository
from infrastructure.schema.umrah_customer_billing_schema import UmrahCustomerBillingBaseSchema, \
    UmrahCustomerBillingResponseSchema, UmrahCustomerBillingListResponse, UmrahCustomerBillingUpdateSchema


async def create_umrah_customer_billing(db: AsyncSession, request: UmrahCustomerBillingBaseSchema, agency_name: str,
                                        username: str):
    try:
        if request.amount <= 0:
            raise HTTPException(status_code=400, detail='Amount must be positive')

        umrah_requisition = await umrah_requisition_repository.get_requisition_by_requisition_code(db=db,
                                                                                                   umrah_requisition_code=request.umrah_requisition_code)

        if not umrah_requisition:
            raise HTTPException(status_code=400, detail='Requisition does not exist')

        request_dict = request.model_dump(exclude_none=True)
        request_dict['agency_name'] = agency_name
        request_dict['created_by'] = username
        request_dict['updated_by'] = username

        total_payment = umrah_requisition.total_payment + request.amount
        requisition_price_update_dict = {
            'total_payment': total_payment,
            'total_due': max(0, umrah_requisition.total_price - total_payment),
        }

        result = await umrah_customer_billing_repository.create_umrah_customer_billing(db=db, request_dict=request_dict,
                                                                                       requisition_price_update_dict=requisition_price_update_dict)
        return UmrahCustomerBillingResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def get_umrah_customer_billing(db: AsyncSession, agency_name: str):
    try:
        result = await umrah_customer_billing_repository.get_umrah_customer_billing(db=db, agency_name=agency_name)
        return [UmrahCustomerBillingListResponse(**row) for row in result]
    except Exception as e:
        raise e


async def update_umrah_customer_billing(db: AsyncSession, request: UmrahCustomerBillingUpdateSchema, agency_name: str,
                                        username: str):
    try:
        umrah_customer_billing = await umrah_customer_billing_repository.get_umrah_customer_billing_by_id(db=db,
                                                                                                          billing_id=request.id)

        if not umrah_customer_billing:
            raise HTTPException(status_code=400, detail='Billing does not exist')

        if umrah_customer_billing.agency_name != agency_name:
            raise HTTPException(status_code=400, detail='Agency name does not match')

        billing_update_dict = {}
        if umrah_customer_billing.amount != request.amount:
            requisition = await umrah_requisition_repository.get_requisition_by_requisition_code(db=db,
                                                                                                 umrah_requisition_code=request.umrah_requisition_code)

            total_payment = requisition.total_payment - umrah_customer_billing.amount + request.amount

            billing_update_dict['total_payment'] = total_payment
            billing_update_dict['total_due'] = max(0, requisition.total_price - total_payment)

        request_dict = request.model_dump(exclude_none=True)
        request_dict['updated_by'] = username
        request_dict['updated_at'] = get_current_time()

        result = await umrah_customer_billing_repository.update_umrah_customer_billing(db=db, request_dict=request_dict,
                                                                                       billing_update_dict=billing_update_dict)
        return UmrahCustomerBillingResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def delete_umrah_customer_billing(db: AsyncSession, agency_name: str, billing_id: int):
    try:
        umrah_customer_billing = await umrah_customer_billing_repository.get_umrah_customer_billing_by_id(db=db,
                                                                                                          billing_id=billing_id)

        if not umrah_customer_billing:
            raise HTTPException(status_code=400, detail='Billing does not exist')
        if umrah_customer_billing.agency_name != agency_name:
            raise HTTPException(status_code=400, detail='Agency name does not match')


        return await umrah_customer_billing_repository.delete_umrah_customer_billing(db=db, billing_id=billing_id, deleted_payment = umrah_customer_billing.amount,
                                                                                     requisition_code = umrah_customer_billing.umrah_requisition_code)
    except Exception as e:
        raise e