from datetime import date

from sqlalchemy import insert, update, select, func, delete, text
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.umrah_b2b_agent_model import UmrahB2BAgentModel
from data.model.umrah_b2b_payment_model import UmrahB2BPayment


async def create_umrah_b2b_payment(db: AsyncSession, request_dict: dict):
    try:
        stmt = (
            insert(UmrahB2BPayment)
            .values(**request_dict)
            .returning(UmrahB2BPayment)
        )

        result = await db.execute(stmt)

        stmt = (
            update(UmrahB2BAgentModel)
            .values(
                total_bill=UmrahB2BAgentModel.total_bill + request_dict['bill'],
                total_credit=UmrahB2BAgentModel.total_credit + request_dict['credit'],
                total_due=func.greatest(
                    0,
                    (UmrahB2BAgentModel.total_bill + request_dict['bill']) -
                    (UmrahB2BAgentModel.total_credit + request_dict['credit'])
                )
            )
            .where(UmrahB2BAgentModel.name == request_dict['b2b_agent_name'])
        )
        await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def get_umrah_b2b_payments(db: AsyncSession, agency_name: str):
    result = await db.execute(
        select(UmrahB2BPayment)
        .where(
            UmrahB2BPayment.agency_name == agency_name
        )
        .order_by(UmrahB2BPayment.id.desc())
    )
    return result.scalars().all()


async def get_umrah_b2b_payment_by_id(db: AsyncSession, payment_id: int):
    result = await db.execute(
        select(UmrahB2BPayment).where(UmrahB2BPayment.id == payment_id)
    )
    return result.scalars().first()


async def update_umrah_b2b_payment(db: AsyncSession, request_dict: dict, b2b_agent_finance_update_dict: dict):
    try:
        stmt = (
            update(UmrahB2BPayment)
            .values(**request_dict)
            .where(UmrahB2BPayment.id == request_dict['id'])
            .returning(UmrahB2BPayment)
        )

        result = await db.execute(stmt)

        b2b_agent_name = b2b_agent_finance_update_dict.pop('b2b_agent_name')
        stmt = (
            update(UmrahB2BAgentModel)
            .values(
                **b2b_agent_finance_update_dict
            )
            .where(UmrahB2BAgentModel.name == b2b_agent_name)
        )
        await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def delete_umrah_b2b_payment(db: AsyncSession, payment_id: int, b2b_agent_finance_update_dict: dict):
    try:
        stmt = (
            delete(UmrahB2BPayment)
            .where(UmrahB2BPayment.id == payment_id)
        )
        await db.execute(stmt)

        b2b_agent_name = b2b_agent_finance_update_dict.pop('b2b_agent_name')
        stmt = (
            update(UmrahB2BAgentModel)
            .values(**b2b_agent_finance_update_dict)
            .where(UmrahB2BAgentModel.name == b2b_agent_name)
        )

        await db.execute(stmt)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise e


async def get_umrah_payments_for_b2b_agent(db: AsyncSession, agency_name: str, b2b_agent_name: str, start_date: date,
                                           end_date: date):
    try:
        query = text("""
                    SELECT 
                        ag.name, 
                        ag.agency_name, 
                        ag.total_bill, 
                        ag.total_credit, 
                        ag.total_due,
                        COALESCE(
                            (
                                SELECT jsonb_agg(
                                    jsonb_build_object(
                                        'invoice_no', p.invoice_no,
                                        'guest_name', p.guest_name,
                                        'bill', p.bill,
                                        'credit', p.credit,
                                        'way_of_payment', p.way_of_payment,
                                        'payment_date', p.payment_date
                                    )
                                )
                                FROM core.umrah_b2b_payements p
                                WHERE p.b2b_agent_name = :b2b_agent_name
                                    AND p.agency_name = :agency_name
                                  AND p.payment_date BETWEEN :start_date AND :end_date
                            ),'[]'::jsonb
                        ) AS payment_list
                    FROM core.umrah_b2b_agents ag
                    WHERE ag.agency_name = :agency_name
                      AND ag.name = :b2b_agent_name
                    GROUP BY ag.name, ag.agency_name, ag.total_bill, ag.total_credit, ag.total_due
                """)

        result = await db.execute(query, {
            "agency_name": agency_name,
            "b2b_agent_name": b2b_agent_name,
            "start_date": start_date,
            "end_date": end_date
        })

        return result.fetchone()
    except Exception as e:
        raise e
