from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.bank_info_model import BankInfoModel


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