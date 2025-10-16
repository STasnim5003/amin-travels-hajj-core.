from sqlalchemy import insert
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