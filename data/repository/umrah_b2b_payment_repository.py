from sqlalchemy import insert, update, select, delete, text, func
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.umrah_b2b_agent_model import UmrahB2BAgentModel
from data.model.umrah_b2b_payment_model import UmrahB2BPayment
from data.model.umrah_requisition_model import UmrahRequisitionModel


async def create_umrah_b2b_payment(db: AsyncSession, request_dict: dict):
    try:
        b2b_agent_name = request_dict['b2b_agent_name']
        amount = request_dict["amount"]
        stmt = (
            insert(UmrahB2BPayment)
            .values(**request_dict)
            .returning(UmrahB2BPayment)
        )

        result = await db.execute(stmt)

        update_stmt = (
            update(UmrahB2BAgentModel)
            .where(
                UmrahB2BAgentModel.name == b2b_agent_name,
                UmrahB2BAgentModel.agency_name == request_dict["agency_name"]
            )
            .values(
                total_credit=UmrahB2BAgentModel.total_credit + amount,
                total_due=func.greatest(
                    0,
                    UmrahB2BAgentModel.total_bill - UmrahB2BAgentModel.total_credit - amount
                )
            )
        )
        await db.execute(update_stmt)

        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def get_umrah_b2b_payments(db: AsyncSession, agency_name: str):
    try:
        query = text("""
                        SELECT
                            uba.name as b2b_agent_name,
                            uba.total_bill,
                            uba.total_credit,
                            uba.total_due,
                            uba.agency_name,
                        
                            (
                                SELECT json_agg(item ORDER BY item_created_at DESC)
                                FROM (
                                    SELECT
                                        json_build_object(
                                            'type', 'requisition',
                                            'amin_office_code', ur.amin_office_code,
                                            'name', ur.name,
                                            'sales_person', ur.sales_person,
                                            'total_price', ur.total_price,
                                            'discount', ur.discount,
                                            'created_at', ur.created_at
                                        ) AS item,
                                        ur.created_at AS item_created_at
                                    FROM core.umrah_requisition ur
                                    WHERE ur.b2b_agent_name = uba.name 
                                        and ur.agency_name = :agency_name 
                                        and ur.requisition_type = 'B2B' 
                                        and ur.is_confirmed = TRUE
                        
                                    UNION ALL
                        
                                    SELECT
                                        json_build_object(
                                            'type', 'payment',
                                            'invoice_no', ubp.invoice_no,
                                            'payment_date', ubp.payment_date,
                                            'amount', ubp.amount,
                                            'payment_way', ubp.way_of_payment,
                                            'created_at', ubp.created_at
                                        ) AS item,
                                        ubp.created_at AS item_created_at
                                    FROM core.umrah_b2b_payements ubp
                                    WHERE ubp.b2b_agent_name = uba.name
                                        and ubp.agency_name = :agency_name
                                ) t
                            ) AS transactions
                        
                        FROM core.umrah_b2b_agents uba
                        WHERE uba.agency_name = :agency_name;
                """)

        result = await db.execute(query, {"agency_name": agency_name})
        return result.mappings().all()
    except Exception as e:
        raise e


async def get_umrah_b2b_payment_by_id(db: AsyncSession, payment_id: int):
    result = await db.execute(
        select(UmrahB2BPayment).where(UmrahB2BPayment.id == payment_id)
    )
    return result.scalars().first()


async def update_umrah_b2b_payment(db: AsyncSession, request_dict: dict, b2b_finance_update: dict):
    try:
        agency_name = b2b_finance_update.pop('agency_name')
        stmt = (
            update(UmrahB2BPayment)
            .values(**request_dict)
            .where(UmrahB2BPayment.id == request_dict['id'])
            .returning(UmrahB2BPayment)
        )

        result = await db.execute(stmt)

        stmt = (
            update(UmrahB2BAgentModel)
            .values(**b2b_finance_update)
            .where(UmrahB2BAgentModel.name == request_dict['b2b_agent_name'], UmrahB2BAgentModel.agency_name == agency_name)
        )
        await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def delete_umrah_b2b_payment(db: AsyncSession, payment_id: int, b2b_finance_update: dict):
    try:
        b2b_agent_name = b2b_finance_update.pop('name')
        agency_name = b2b_finance_update.pop('agency_name')
        stmt = (
            delete(UmrahB2BPayment)
            .where(UmrahB2BPayment.id == payment_id)
        )
        await db.execute(stmt)

        stmt = (
            update(UmrahB2BAgentModel)
            .values(**b2b_finance_update)
            .where(UmrahB2BAgentModel.name == b2b_agent_name, UmrahB2BAgentModel.agency_name == agency_name)
        )

        await db.execute(stmt)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise e


async def get_umrah_payments_for_b2b_agent(db: AsyncSession, agency_name: str, b2b_agent_name: str):
    try:
        query = text("""
                    SELECT
                        ur.b2b_agent_name,
                        SUM(ur.total_price) AS total_price,
                        SUM(ur.total_payment) AS total_payment,
                        SUM(ur.total_due) AS total_due,
                    
                        COALESCE(
                            (
                                SELECT jsonb_agg(
                                    jsonb_build_object(
                                        'invoice_no', p.invoice_no,
                                        'way_of_payment', p.way_of_payment,
                                        'payment_date', p.payment_date,
                                        'amin_office_code', p.amin_office_code,
                                        'amount', p.amount,
                                        'id', p.id,
                                        'description', p.description
                                    )
                                    ORDER BY p.id DESC
                                )
                                FROM core.umrah_b2b_payements p
                                WHERE p.b2b_agent_name = ur.b2b_agent_name
                                  AND p.agency_name = ur.agency_name
                            ),
                            '[]'::jsonb
                        ) AS payment_list
                    
                    FROM core.umrah_requisition ur
                    WHERE ur.agency_name = :agency_name
                      AND ur.b2b_agent_name = :b2b_agent_name
                      AND ur.is_confirmed = TRUE
                    GROUP BY
                        ur.b2b_agent_name,
                        ur.agency_name;
                """)

        result = await db.execute(query, {
            "agency_name": agency_name,
            "b2b_agent_name": b2b_agent_name
        })

        return result.fetchone()
    except Exception as e:
        raise e


async def get_umrah_b2b_billing_invoice(db: AsyncSession, amin_office_code: str):
    try:
        query = text("""
                SELECT 
                    ur.amin_office_code,
                    ur.b2b_agent_name,
                    ur.sales_person,
                    ur.name,
                    ur.mobile_no,
                    ur.total_price,
                    ur.total_due,
                    ur.total_payment,
                    ur.discount,
                    ur.adult_traveller,
                    ur.other_traveller,
                    ur.per_head_price_adult,
                    ur.per_head_price_child,
                    ur.per_head_price_infant,
                    ur.agency_name
                FROM core.umrah_requisition ur
                WHERE ur.amin_office_code = :amin_office_code
            """)

        result = await db.execute(
            query,
            {"amin_office_code": amin_office_code}
        )

        row = result.mappings().first()
        return row

    except Exception as e:
        raise e
