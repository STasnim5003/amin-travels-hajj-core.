from sqlalchemy import insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.umrah_customer_billing_model import UmrahCustomerBillingModel
from data.model.umrah_requisition_model import UmrahRequisitionModel


async def create_umrah_customer_billing(db: AsyncSession, request_dict: dict, requisition_price_update_dict:dict):
    try:
        stmt = (
            insert(UmrahCustomerBillingModel)
            .values(**request_dict)
            .returning(UmrahCustomerBillingModel)
        )

        result = await db.execute(stmt)

        stmt = (
            update(UmrahRequisitionModel)
            .values(**requisition_price_update_dict)
            .where(UmrahRequisitionModel.invoice_no == request_dict['invoice_no'])
        )
        await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e
