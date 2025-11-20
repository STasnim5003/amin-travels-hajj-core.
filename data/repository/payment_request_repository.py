from typing import List

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.payment_request_model import PaymentRequestModel


async def create_payment_request(db:AsyncSession, request_dict: dict):
    try:
        stmt = (
            insert(PaymentRequestModel)
            .values(**request_dict)
            .returning(PaymentRequestModel)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e

async def get_payment_requests(db:AsyncSession, agency_names:List[str]):
    try:
        stmt = (
            select(PaymentRequestModel)
            .where(PaymentRequestModel.agency_name.in_(agency_names))
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        raise e

async def get_payment_request_by_id(db:AsyncSession, payment_request_id: int):
    try:
        stmt = (
            select(PaymentRequestModel)
            .where(PaymentRequestModel.id == payment_request_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except Exception as e:
        raise e

async def update_payment_request(db:AsyncSession, request_dict: dict):
    try:
        stmt = (
            update(PaymentRequestModel)
            .where(PaymentRequestModel.id == request_dict['id'])
            .values(**request_dict)
            .returning(PaymentRequestModel)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e