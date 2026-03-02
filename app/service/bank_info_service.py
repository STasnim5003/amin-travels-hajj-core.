from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.utils.get_current_time import get_current_time
from data.repository import bank_info_repository
from infrastructure.schema.bank_info_schema import BankInfoBaseSchema, BankInfoUpdateSchema, BankInfoResponseSchema


async def create_bank_info(
        db:AsyncSession,
        request: BankInfoBaseSchema,
        agency_name : str,
        username:str
):
    try:
        request_dict = request.model_dump(exclude_unset=True)
        request_dict['agency_name'] = agency_name
        request_dict['created_by'] = username
        request_dict['updated_by'] = username

        return await bank_info_repository.create_bank_info(db, request_dict)
    except Exception as e:
        raise e

async def get_bank_info(
        db:AsyncSession, agency_name : str
):
    try:
        banks = await bank_info_repository.get_bank_info(db, agency_name)
        return [BankInfoResponseSchema.model_validate(result) for result in banks]
    except Exception as e:
        raise e

async def update_bank_info(
        db: AsyncSession, update_request: BankInfoUpdateSchema, agency_name : str, username:str
):
    try:
        bank = await bank_info_repository.get_bank_info_by_id(db, update_request.id)
        if not bank or bank.agency_name != agency_name:
            raise HTTPException(status_code=400, detail="Bank Not Found")

        updated_dict = update_request.model_dump(exclude_none=True)
        updated_dict['updated_by'] = username
        updated_dict['updated_at'] = get_current_time()
        updated_bank = await bank_info_repository.update_bank_info(db, updated_dict)
        return BankInfoResponseSchema.model_validate(updated_bank)
    except Exception as e:
        raise e

async def delete_bank_info(db:AsyncSession, bank_id : int, agency_name : str):
    try:
        bank = await bank_info_repository.get_bank_info_by_id(db=db, bank_id=bank_id)
        if not bank or bank.agency_name != agency_name:
            raise HTTPException(status_code=400, detail="Bank Not Found")

        result = await bank_info_repository.delete_bank_info(db=db, bank_id=bank_id)
        if result:
            banks = await bank_info_repository.get_bank_info(db=db, agency_name=agency_name)
            return [BankInfoResponseSchema.model_validate(bank) for bank in banks]

    except Exception as e:
        raise e

async def get_bank_info_by_id(db:AsyncSession, bank_id:int, agency_name : str):
    try:
        bank = await bank_info_repository.get_bank_info_by_id(db=db, bank_id=bank_id)
        if not bank or bank.agency_name != agency_name:
            raise HTTPException(status_code=400, detail="Bank Not Found")
        return BankInfoResponseSchema.model_validate(bank)

    except Exception as e:
        raise e