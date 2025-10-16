from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import bank_info_repository
from infrastructure.schema.bank_info_schema import BankInfoBaseSchema


async def create_bank_info(
        db:AsyncSession,
        request: BankInfoBaseSchema,
        agency_name : str
):
    try:
        request_dict = request.model_dump(exclude_unset=True)
        request_dict['agency_name'] = agency_name
        request_dict['created_by'] = agency_name
        request_dict['updated_by'] = agency_name

        return await bank_info_repository.create_bank_info(db, request_dict)
    except Exception as e:
        raise e

async def get_bank_info(
        db:AsyncSession, agency_name : str
):
    try:
        return await bank_info_repository.get_bank_info(db, agency_name)
    except Exception as e:
        raise e