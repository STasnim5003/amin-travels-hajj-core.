from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import admin_repository
from infrastructure.schema.admin_schema import AdminBaseSchema, AdminResponseSchema

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

async def create_admin(admin_request_schema: AdminBaseSchema, db: AsyncSession) -> AdminResponseSchema:
    hashed_password = hash_password(admin_request_schema.password)
    admin_request_schema.password = hashed_password
    result = await admin_repository.insert_admin(admin_request_schema, db=db)
    return result

# async def get_users( db: AsyncSession, name:str=None, whats_app_no: str=None) -> List[UserResponseSchema]:
#     result = await user_repository.get_users(name=name, whats_app_no=whats_app_no, db=db)
#     return result
