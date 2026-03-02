from fastapi import HTTPException
from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.bank_info_model import BankInfoModel
from infrastructure.schema.bank_info_schema import BankInfoUpdateSchema


async def create_bank_info(db:AsyncSession, request: dict):
    try:
        stmt = (
            insert(BankInfoModel)
            .values(**request)
            .returning(BankInfoModel)
        )

        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one()
    except Exception as e:
        await db.rollback()
        raise e

async def get_bank_info(
        db:AsyncSession,
        agency_name: str
):
    try:
        stmt = (
            select(BankInfoModel).where(BankInfoModel.agency_name == agency_name)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        raise e

async def get_bank_info_by_id(db: AsyncSession, bank_id: int):
    try:
        result = await db.execute(
            select(BankInfoModel).where(BankInfoModel.id == bank_id)
        )
        return result.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(status_code = 400, detail= str(e))

async def update_bank_info(db: AsyncSession, update_request:dict):
    try:
        stmt = (
            update(BankInfoModel)
            .where(BankInfoModel.id == update_request['id'])
            .values(**update_request)
            .returning(BankInfoModel)
        )

        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one()
    except Exception as e:
        raise HTTPException(status_code = 400, detail= str(e))


async def delete_bank_info(db:AsyncSession, bank_id:int):
    try:
        stmt = (
            delete(BankInfoModel)
            .where(BankInfoModel.id == bank_id)
        )

        await db.execute(stmt)
        await db.commit()
        return True
    except Exception as e:
        raise HTTPException(status_code = 400, detail= str(e))