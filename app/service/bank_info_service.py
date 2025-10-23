from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from data.repository import bank_info_repository
from infrastructure.schema.bank_info_schema import BankInfoBaseSchema, BankInfoUpdateSchema


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

async def update_bank_info(
        db: AsyncSession, update_request: BankInfoUpdateSchema, agency_name : str
):
    try:
        bank = await bank_info_repository.get_bank_info_by_id(db, update_request.id)
        if not bank or bank.agency_name != agency_name:
            raise HTTPException(status_code=400, detail="Bank Not Found")

        updated_bank = await bank_info_repository.update_bank_info(db, update_request)
        return updated_bank
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
            return banks

    except Exception as e:
        raise e

async def get_bank_info_by_id(db:AsyncSession, bank_id:int, agency_name : str):
    try:
        bank = await bank_info_repository.get_bank_info_by_id(db=db, bank_id=bank_id)
        if not bank or bank.agency_name != agency_name:
            raise HTTPException(status_code=400, detail="Bank Not Found")
        return bank

    except Exception as e:
        raise e