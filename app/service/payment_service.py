from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import payment_repository
from infrastructure.schema.payment_schema import PaymentSchema


async def create_payable_for_group_leader(db:AsyncSession, payment_request:PaymentSchema, agency_name:str):
    try:
        return await payment_repository.create_payable_for_group_leader(db, payment_request, agency_name)
    except Exception as e:
        raise e