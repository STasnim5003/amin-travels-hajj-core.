from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.payment_category_model import PaymentCategoryModel
from infrastructure.schema.payment_category_schema import PaymentCategoryBase



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
        db:AsyncSession,
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