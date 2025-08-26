from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import program_repository
from infrastructure.schema.program_schema import ProgramCreateSchema, \
    ProgramRegistrationCreateSchema, PaginatedProgramParticipantsResponseSchema, ProgramRegistrationResponse, \
    ProgramUpdateSchema


async def create_get_together_program(program_request_schema: ProgramCreateSchema, db: AsyncSession):
    result = await program_repository.insert_get_together_program(program_request_schema, db)
    return result


async def create_get_together_registration(registration_request_schema: ProgramRegistrationCreateSchema,
                                           db: AsyncSession):
    existing_program = await program_repository.find_get_together_program_by_id(
        registration_request_schema.get_together_program_id, db)
    if existing_program is None:
        raise ValueError("Program is not Found!")

    result = await program_repository.insert_get_together_registration(registration_request_schema, db)
    return result


async def get_active_programs(db: AsyncSession, program_type: str, is_active: bool):
    programs = await program_repository.get_available_programs(db, program_type, is_active)
    return programs


async def fetch_participants_by_program_id(
        program_id: int,
        db: AsyncSession,
        page: int,
        limit: int
) -> PaginatedProgramParticipantsResponseSchema:
    skip = (page - 1) * limit
    participants, total = await program_repository.get_participants_by_program_id(program_id, db, skip, limit)

    participants_models = [
        ProgramRegistrationResponse.model_validate(p) for p in participants
    ]

    return PaginatedProgramParticipantsResponseSchema(
        participants=participants_models,
        total=total,
        page=page,
        limit=limit
    )


async def get_all_programs(db: AsyncSession, program_type: str):
    programs = await program_repository.get_all_programs(db, program_type)
    return programs

async def update_program(db:AsyncSession, program_id:int, program_data:ProgramUpdateSchema):
    db_program = await program_repository.find_program_by_id(program_id, db)
    if db_program is None:
        raise ValueError("Program is not Found!")

    updated_program = await program_repository.update_program(db, db_program, program_data)
    return updated_program

async def delete_program(db:AsyncSession, program_id:int):
    program = await program_repository.find_program_by_id(program_id, db)

    if program is None:
        raise ValueError("Program is not Found!")
    await program_repository.delete_program(db, program)