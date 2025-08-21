from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import get_together_repository
from infrastructure.schema.get_together_schema import GetTogetherProgramCreateSchema, \
    GetTogetherRegistrationCreateSchema, PaginatedGetTogetherParticipantsResponseSchema, GetTogetherRegistrationResponse


async def create_get_together_program(program_request_schema: GetTogetherProgramCreateSchema, db: AsyncSession):
    result = await get_together_repository.insert_get_together_program(program_request_schema, db)
    return result


async def create_get_together_registration(registration_request_schema: GetTogetherRegistrationCreateSchema, db:AsyncSession):

    existing_program = await get_together_repository.find_get_together_program_by_id(registration_request_schema.get_together_program_id, db)
    if existing_program is None:
        raise ValueError("Program is not Found!")

    result = await get_together_repository.insert_get_together_registration(registration_request_schema, db)
    return result


async def get_active_programs(db:AsyncSession):
    programs = await get_together_repository.get_available_programs(db)
    return programs

async def fetch_participants_by_program_id(
        program_id: int,
        db: AsyncSession,
        page: int,
        limit: int
) -> PaginatedGetTogetherParticipantsResponseSchema:
    skip = (page - 1) * limit
    participants, total = await get_together_repository.get_participants_by_program_id(program_id, db, skip, limit)

    participants_models = [
        GetTogetherRegistrationResponse.model_validate(p) for p in participants
    ]

    return PaginatedGetTogetherParticipantsResponseSchema(
        participants=participants_models,
        total=total,
        page=page,
        limit=limit
    )
