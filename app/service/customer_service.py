from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import customer_repository
from infrastructure.schema.customer_schema import CustomerCreateSchema, CustomerAppliedForRegistrationSchema
from infrastructure.schema.pilgrim_data_schema import PilgrimDataResponseSchema


async def create_customer(db:AsyncSession, customer:CustomerCreateSchema,group_name:str,username:str):
    try:
        response = await customer_repository.create_customer(db=db, customer=customer, group_name=group_name,username=username)
        return PilgrimDataResponseSchema.model_validate(response)
    except Exception as e:
        raise

async def customer_applied_for_registered(db:AsyncSession, tracking_ids:CustomerAppliedForRegistrationSchema, group_name:str,username:str):
    try:
        response = await customer_repository.customer_applied_for_registration(db=db, tracking_ids=tracking_ids, group_name=group_name,username=username)
        return [PilgrimDataResponseSchema.model_validate(row) for row in response]

    except Exception as e:
        raise