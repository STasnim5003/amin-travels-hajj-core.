from typing import List

from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.admin_model import AdminModel
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
        admin_update_data = {}
        if "bdt" in request_dict:
            admin_update_data["bdt"] = request_dict.pop("bdt")
        if "sar" in request_dict:
            admin_update_data["sar"] = request_dict.pop("sar")

        stmt = (
            update(PaymentRequestModel)
            .where(PaymentRequestModel.id == request_dict['id'])
            .values(**request_dict)
            .returning(PaymentRequestModel)
        )
        result = await db.execute(stmt)

        if admin_update_data:
            admin_stmt = (
                update(AdminModel)
                .where(AdminModel.agency_name == request_dict["agency_name"])
                .values(**admin_update_data)
            )
            await db.execute(admin_stmt)

        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def delete_payment_request(db, payment_request_id):
    try:
        stmt = (
            delete(PaymentRequestModel)
            .where(PaymentRequestModel.id == payment_request_id)
        )

        await db.execute(stmt)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise e
