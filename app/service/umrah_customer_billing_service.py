from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from data.repository import umrah_customer_billing_repository, umrah_requisition_repository
from infrastructure.schema.umrah_customer_billing_schema import UmrahCustomerBillingBaseSchema, \
    UmrahCustomerBillingResponseSchema


async def create_umrah_customer_billing(db: AsyncSession, request: UmrahCustomerBillingBaseSchema, agency_name: str,
                                        username: str):
    try:
        if request.amount <= 0:
            raise HTTPException(status_code=400, detail='Amount must be positive')

        umrah_requisition = await umrah_requisition_repository.get_requisition_by_invoice_no(db=db,
                                                                                             invoice_no=request.invoice_no)

        if not umrah_requisition:
            raise HTTPException(status_code=400, detail='Invoice does not exist')

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
