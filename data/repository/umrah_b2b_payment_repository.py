from sqlalchemy import insert, update, select, func, delete
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


async def update_umrah_b2b_payment(db: AsyncSession, request_dict: dict, b2b_agent_finance_update_dict:dict):
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


async def delete_umrah_b2b_payment(db: AsyncSession, payment_id: int, b2b_agent_finance_update_dict:dict):
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
