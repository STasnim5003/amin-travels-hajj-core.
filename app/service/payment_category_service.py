from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from data.repository import payment_category_repository
from infrastructure.schema.payment_category_schema import PaymentCategoryBase, PaymentCategoryUpdateSchema, \
    PaymentCategoryResponse


async def create_payment_category(
        db: AsyncSession,
        request: PaymentCategoryBase,
        agency_name : str,
        username : str
):
    try:
        request_dict = request.model_dump(exclude_unset=True)
        request_dict['agency_name'] = agency_name
        request_dict['created_by'] = username
        request_dict['updated_by'] = username
        return await payment_category_repository.create_payment_category(db, request_dict)
    except Exception as e:
        raise e

async def get_payment_category(db:AsyncSession,agency_name:str):
    try:
        payment_categories = await payment_category_repository.get_payment_categories(db, agency_name)
        return [PaymentCategoryResponse.model_validate(category) for category in payment_categories]
    except Exception as e:
        raise e

async def get_payment_category_by_id(db: AsyncSession, payment_category_id: int, agency_name: str):
    try:
        result = await payment_category_repository.get_payment_category_by_id(db=db, payment_category_id=payment_category_id, agency_name=agency_name)
        if not result:
            raise HTTPException(status_code=404, detail='Payment category not found')
        return result
    except Exception as e:
        raise e

async def update_payment_category(db:AsyncSession, update_request: PaymentCategoryUpdateSchema, agency_name : str, username:str):
    try:
        result = await payment_category_repository.get_payment_category_by_id(db=db, payment_category_id=update_request.id, agency_name=agency_name)
        if not result:
            raise HTTPException(status_code=400, detail='Payment category not found')

        update_request_dict = update_request.model_dump(exclude_none=True)
        update_request_dict["updated_by"] = username
        update_request_dict["updated_at"] = get_current_time()

        updated_payment_category = await payment_category_repository.update_payment_category(db=db, update_request_dict=update_request_dict)
        return PaymentCategoryResponse.model_validate(updated_payment_category)
    except Exception as e:
        raise e

async def delete_payment_category(db:AsyncSession, payment_category_id:int, agency_name:str):
    try:
        payment_category = await payment_category_repository.get_payment_category_by_id(db=db, payment_category_id=payment_category_id, agency_name=agency_name)
        if not payment_category:
            raise HTTPException(status_code=400, detail='Payment category not found')
        await payment_category_repository.delete_payment_category(db=db, payment_category_id=payment_category_id)

        payment_categories = await payment_category_repository.get_payment_categories(db, agency_name)
        return [PaymentCategoryResponse.model_validate(category) for category in payment_categories]

    except Exception as e:
        raise e
