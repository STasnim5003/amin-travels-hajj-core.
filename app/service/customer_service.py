from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import customer_repository
from infrastructure.schema.customer_schema import CustomerCreateSchema
from infrastructure.schema.pilgrim_data_schema import PilgrimDataResponseSchema


async def create_customer(db:AsyncSession, customer:CustomerCreateSchema,group_name:str):
    try:
        response = await customer_repository.create_customer(db=db, customer=customer, group_name=group_name)
        return PilgrimDataResponseSchema.model_validate(response)
    except Exception as e:
        raise