from sqlalchemy import insert, update, text, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.umrah_customer_billing_model import UmrahCustomerBillingModel
from data.model.umrah_requisition_model import UmrahRequisitionModel


async def create_umrah_customer_billing(db: AsyncSession, request_dict: dict, requisition_price_update_dict: dict):
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
            .where(UmrahRequisitionModel.umrah_requisition_code == request_dict['umrah_requisition_code'])
        )
        await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def get_umrah_customer_billing(db: AsyncSession, agency_name: str):
    try:
        query = text("""
                SELECT 
                    ur.umrah_requisition_code,
                    ur.invoice_no,
                    ur.name,
                    ur.total_price,
                    ur.total_payment,
                    ur.total_due,

                    json_agg(
                        json_build_object(
                            'amount', ucb.amount,
                            'description', ucb.description,
                            'way_of_payment', ucb.way_of_payment,
                            'date', ucb.date,
                            'remarks', ucb.remarks,
                            'id', ucb.id
                        )
                        ORDER BY ucb.id
                    ) AS billing_list

                FROM core.umrah_requisition ur
                LEFT JOIN core.umrah_customer_billing ucb
                    ON ur.umrah_requisition_code = ucb.umrah_requisition_code

                WHERE ur.agency_name = :agency_name

                GROUP BY 
                    ur.umrah_requisition_code,
                    ur.invoice_no,
                    ur.name,
                    ur.total_price,
                    ur.total_payment,
                    ur.total_due
            """)

        result = await db.execute(query, {"agency_name": agency_name})
        rows = result.mappings().all()

        return rows
    except Exception as e:
        raise e


async def get_umrah_customer_billing_by_id(db: AsyncSession, billing_id: int):
    try:
        stmt = (
            select(UmrahCustomerBillingModel)
            .where(UmrahCustomerBillingModel.id == billing_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except Exception as e:
        raise e


async def update_umrah_customer_billing(db: AsyncSession, request_dict: dict, billing_update_dict: dict):
    try:
        stmt = (
            update(UmrahCustomerBillingModel)
            .values(**request_dict)
            .where(UmrahCustomerBillingModel.id == request_dict['id'])
            .returning(UmrahCustomerBillingModel)
        )

        result = await db.execute(stmt)

        if billing_update_dict:
            stmt = (
                update(UmrahRequisitionModel)
                .values(**billing_update_dict)
                .where(UmrahRequisitionModel.umrah_requisition_code == request_dict['umrah_requisition_code'])
            )
            await db.execute(stmt)

        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def delete_umrah_customer_billing(db: AsyncSession, billing_id: int, deleted_payment: float,
                                        requisition_code: str):
    try:
        stmt = (
            delete(UmrahCustomerBillingModel)
            .where(UmrahCustomerBillingModel.id == billing_id)
        )

        await db.execute(stmt)

        stmt = (
            update(UmrahRequisitionModel)
            .where(UmrahRequisitionModel.umrah_requisition_code == requisition_code)
            .values(
                total_payment=UmrahRequisitionModel.total_payment - deleted_payment,
                total_due=UmrahRequisitionModel.total_due + deleted_payment
            )
        )

        await db.execute(stmt)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise e


async def get_umrah_customer_billing_invoice_data(db:AsyncSession, umrah_requisition_code:str):
    try:
        query = text("""
                SELECT 
                    ur.umrah_requisition_code,
                    ur.invoice_no,
                    ur.name,
                    ur.mobile_no,
                    ur.total_price,
                    ur.total_due,
                    ur.total_payment,
                    ur.adult_traveller,
                    ur.other_traveller,
                    ur.per_head_price_adult,
                    ur.per_head_price_child,
                    ur.per_head_price_infant,
                    ur.agency_name
                FROM core.umrah_requisition ur
                WHERE ur.umrah_requisition_code = :umrah_requisition_code
            """)

        result = await db.execute(
            query,
            {"umrah_requisition_code": umrah_requisition_code}
        )

        row = result.mappings().first()
        return row

    except Exception as e:
        raise e