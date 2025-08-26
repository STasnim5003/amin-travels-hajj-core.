import logging
from datetime import date

from sqlalchemy import insert, select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.program_model import ProgramBaseModel, ProgramRegistrationBaseModel
from infrastructure.schema.program_schema import ProgramCreateSchema, ProgramRegistrationCreateSchema, \
    ProgramRegistrationResponse, ProgramResponseSchema, ProgramUpdateSchema


async def insert_get_together_program(get_together: ProgramCreateSchema, db: AsyncSession):
    program_data = get_together.model_dump(exclude_unset=True, exclude_none=True)
    query = insert(ProgramBaseModel).values(**program_data).returning(ProgramBaseModel)
    try:
        result = await db.execute(query)
        await db.commit()

        row = result.fetchone()
        if row is None:
            raise ValueError("Program Creation Failed")

        program_model_instance = row._mapping['ProgramBaseModel']
        return ProgramResponseSchema.model_validate(program_model_instance.__dict__)

    except Exception as e:
        await db.rollback()
        logging.error("Error : ", str(e))
        raise


async def find_program_by_id(id: int, db: AsyncSession):
    result = await db.execute(
        select(ProgramBaseModel)
        .where(ProgramBaseModel.id == id)
    )
    program = result.scalars().first()
    return program


async def insert_get_together_registration(get_together_registration: ProgramRegistrationCreateSchema,
                                           db: AsyncSession):
    try:
        registration = ProgramRegistrationBaseModel(
            **get_together_registration.model_dump(exclude_unset=True, exclude_none=True))

        db.add(registration)
        await db.commit()
        await db.refresh(registration)

        return ProgramRegistrationResponse.model_validate(registration)

    except Exception as e:
        await db.rollback()
        logging.error("Error : ", str(e))
        raise


async def get_available_programs(db: AsyncSession, program_type: str, is_active: bool):
    today = date.today()

    query = (
        select(ProgramBaseModel)
        .where(
            and_(
                ProgramBaseModel.registration_deadline > today,
                ProgramBaseModel.program_type == program_type,
                ProgramBaseModel.is_active == is_active
            )
        )
        .order_by(ProgramBaseModel.registration_deadline.asc())
    )

    result = await db.execute(query)
    programs = result.scalars().all()

    return [ProgramResponseSchema.model_validate(program) for program in programs]


async def get_participants_by_program_id(
        program_id: int,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
):
    total_query = (
        select(func.count(ProgramRegistrationBaseModel.id))
        .where(ProgramRegistrationBaseModel.get_together_program_id == program_id)
    )
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()

    # ✅ Paginated participants
    query = (
        select(ProgramRegistrationBaseModel)
        .where(ProgramRegistrationBaseModel.get_together_program_id == program_id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    participants = result.scalars().all()

    # ✅ Fetch program only once
    program_query = select(ProgramBaseModel).where(ProgramBaseModel.id == program_id)
    program_result = await db.execute(program_query)
    program = program_result.scalar_one_or_none()

    # ✅ Attach program to each participant
    for p in participants:
        p.program = program

    return participants, total


async def get_all_programs(db, program_type):
    query = (
        select(ProgramBaseModel)
        .where(ProgramBaseModel.program_type == program_type)
        .order_by(ProgramBaseModel.registration_deadline.asc())
    )

    result = await db.execute(query)
    programs = result.scalars().all()

    return [ProgramResponseSchema.model_validate(program) for program in programs]


async def update_program(db: AsyncSession, db_program: ProgramBaseModel, program_data: ProgramUpdateSchema):
    update_data = program_data.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_program, key, value)

    await db.commit()
    await db.refresh(db_program)
    return db_program

async def delete_program(db:AsyncSession, program:ProgramBaseModel):
    await db.delete(program)
    await db.commit()