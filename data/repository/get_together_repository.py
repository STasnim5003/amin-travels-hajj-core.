import logging

from sqlalchemy import insert, select
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from data.model.get_together_model import GetTogetherProgramCreate, GetTogetherRegistration
from infrastructure.schema.get_together_schema import GetTogetherProgramCreateSchema, GetTogetherProgramResponse, \
    GetTogetherRegistrationCreateSchema, GetTogetherRegistrationResponse


async def insert_get_together_program(get_together : GetTogetherProgramCreateSchema, db: AsyncSession):
    program_data = get_together.model_dump(exclude_unset=True, exclude_none=True)
    query = insert(GetTogetherProgramCreate).values(**program_data).returning(GetTogetherProgramCreate)
    try:
        result = await db.execute(query)
        await db.commit()

        row = result.fetchone()
        if row is None:
            raise ValueError("Program Creation Failed")

        program_model_instance = row._mapping['GetTogetherProgramCreate']
        return GetTogetherProgramResponse.model_validate(program_model_instance.__dict__)

    except Exception as e:
        await db.rollback()
        logging.error("Error : ", str(e))
        raise

async def find_get_together_program_by_id(id: int, db: AsyncSession):
    result = await db.execute(
        select(GetTogetherProgramCreate)
        .where(GetTogetherProgramCreate.id == id)
    )
    program = result.scalars().first()
    return program

async def insert_get_together_registration(get_together_registration: GetTogetherRegistrationCreateSchema, db:AsyncSession):
    try:
        registration = GetTogetherRegistration(
            **get_together_registration.model_dump(exclude_unset=True, exclude_none=True))

        db.add(registration)
        await db.commit()
        await db.refresh(registration)

        return GetTogetherRegistrationResponse.model_validate(registration)

    except Exception as e:
        await db.rollback()
        logging.error("Error : ", str(e))
        raise