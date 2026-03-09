from fastapi import HTTPException
from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from data.model.payment_category_model import PaymentCategoryModel
from infrastructure.schema.payment_category_schema import PaymentCategoryBase, PaymentCategoryUpdateSchema


async def create_payment_category(
        db: AsyncSession,
        request: dict
):
    try:
        stmt = (
            insert(PaymentCategoryModel)
            .values(**request)
            .returning(PaymentCategoryModel)
        )

        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one()
    except Exception as e:
        await db.rollback()
        raise e


async def get_payment_categories(
        db: AsyncSession,
        agency_name: str
):
    try:
        stmt = (
            select(PaymentCategoryModel).where(PaymentCategoryModel.agency_name == agency_name)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        raise e


async def get_payment_category_by_id(
        db: AsyncSession, payment_category_id: int, agency_name: str
):
    try:
        stmt = (
            select(PaymentCategoryModel)
            .where(PaymentCategoryModel.id == payment_category_id, PaymentCategoryModel.agency_name == agency_name)
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except Exception as e:
        raise e


async def update_payment_category(db: AsyncSession, update_request_dict : dict):
    try:

        stmt = (
            update(PaymentCategoryModel)
            .where(PaymentCategoryModel.id == update_request_dict['id'])
            .values(**update_request_dict)
            .returning(PaymentCategoryModel)
        )

        result = await db.execute(stmt)
        updated_record = result.scalar_one_or_none()

        if not updated_record:
            raise HTTPException(status_code=400, detail="Payment category not found")

        await db.commit()
        return updated_record

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def delete_payment_category(db: AsyncSession, payment_category_id: int):
    try:
        stmt = (
            delete(PaymentCategoryModel).where(PaymentCategoryModel.id == payment_category_id)
        )
        await db.execute(stmt)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
