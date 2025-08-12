from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.utils.utils import hash_password, verify_password, create_access_token, create_refresh_token
from data.repository import admin_repository
from infrastructure.schema.admin_schema import AdminBaseSchema, AdminResponseSchema


async def create_admin(admin_request_schema: AdminBaseSchema, db: AsyncSession) -> AdminResponseSchema:
    hashed_password = hash_password(admin_request_schema.password)
    admin_request_schema.password = hashed_password
    result = await admin_repository.insert_admin(admin_request_schema, db=db)
    return result

# async def get_users( db: AsyncSession, name:str=None, whats_app_no: str=None) -> List[UserResponseSchema]:
#     result = await user_repository.get_users(name=name, whats_app_no=whats_app_no, db=db)
#     return result

async def admin_login(db : AsyncSession, request_credential: OAuth2PasswordRequestForm ):
    user = await admin_repository.get_admin_by_username(db, username=request_credential.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )

    if not verify_password(request_credential.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )

    access_token = create_access_token(subject=user.user_name, role=user.role)
    refresh_token = create_refresh_token(subject=user.user_name, role=user.role)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }