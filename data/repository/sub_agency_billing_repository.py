
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, insert, select, delete

from data.model.admin_model import AdminModel
from data.model.payment_request_model import PaymentRequestModel


async def create_sub_agency_bill(db:AsyncSession, request_dict:dict):
    try:
        admin_update_data = {}
        if "bdt" in request_dict:
            admin_update_data["bdt"] = request_dict.pop("bdt")
        if "sar" in request_dict:
            admin_update_data["sar"] = request_dict.pop("sar")

        stmt = (
            insert(PaymentRequestModel)
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


async def get_sub_agency_bill(db: AsyncSession, agency_names: List[str]):
    try:
        stmt = (
            select(PaymentRequestModel)
            .where(
                PaymentRequestModel.agency_name.in_(agency_names),
                PaymentRequestModel.payment_way == "Bill"
            )
            .order_by(PaymentRequestModel.id.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        raise e

async def get_sub_agency_bill_by_id(db:AsyncSession, bill_id:int):
    try:
        stmt = (
            select(PaymentRequestModel)
            .where(
                PaymentRequestModel.id == bill_id,
                PaymentRequestModel.payment_way == "Bill"
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except Exception as e:
        raise e


async def update_sub_agency_bill(db:AsyncSession, request_dict:dict):
    try:
        stmt = (
            update(PaymentRequestModel)
            .values(**request_dict)
            .where(PaymentRequestModel.id == request_dict.get("id"))
            .returning(PaymentRequestModel)
        )

        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def delete_sub_agency_bill(db:AsyncSession, bill_id:int):
    try:
        stmt = (
            delete(PaymentRequestModel)
            .where(PaymentRequestModel.id == bill_id)
        )
        await db.execute(stmt)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise e