from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import payment_category_repository
from infrastructure.schema.payment_category_schema import PaymentCategoryBase


async def create_payment_category(
        db: AsyncSession,
        request: PaymentCategoryBase,
        agency_name : str
):
    try:
        request_dict = request.model_dump(exclude_unset=True)
        request_dict['agency_name'] = agency_name
        return await payment_category_repository.create_payment_category(db, request_dict)
    except Exception as e:
        raise e

async def get_payment_category(
        db:AsyncSession,
        agency_name:str
):
    try:
        return await payment_category_repository.get_payment_categories(db, agency_name)
    except Exception as e:
        raise e