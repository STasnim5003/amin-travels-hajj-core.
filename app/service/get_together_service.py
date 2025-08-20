from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import get_together_repository
from infrastructure.schema.get_together_schema import GetTogetherProgramCreateSchema, \
    GetTogetherRegistrationCreateSchema


async def create_get_together_program(program_request_schema: GetTogetherProgramCreateSchema, db: AsyncSession):
    result = await get_together_repository.insert_get_together_program(program_request_schema, db)
    return result


async def create_get_together_registration(registration_request_schema: GetTogetherRegistrationCreateSchema, db:AsyncSession):

    existing_program = await get_together_repository.find_get_together_program_by_id(registration_request_schema.get_together_program_id, db)
    if existing_program is None:
        raise ValueError("Program is not Found!")

    result = await get_together_repository.insert_get_together_registration(registration_request_schema, db)
    return result
