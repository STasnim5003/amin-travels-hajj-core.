from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.utils import hash_password, verify_password, create_access_token_for_admin_user, \
    create_refresh_token_for_admin_user
from data.repository import admin_user_repository
from infrastructure.schema.admin_schema import AdminResponseSchema
from infrastructure.schema.admin_user_schema import AdminUserCreate, AdminUserResponse


async def list_users(db: AsyncSession, agency_name : str):
    return await admin_user_repository.get_all(db, agency_name)



async def get_user(db: AsyncSession, user_id: int, agency_name : str):
    user = await admin_user_repository.get_by_id(db, user_id, agency_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def create_user(db: AsyncSession, user_data: AdminUserCreate, agency_name:str):
    hashed_password = hash_password(user_data.password)
    user_data.password = hashed_password

    role_code_map = {
        "GROUP_LEADER": "GL",
        "STAFF": "ST",
        "SAUDI_REPRESENTATIVE": "SR"
    }

    code_suffix = role_code_map.get(user_data.role, "GEN")
    code = f"{agency_name}_{code_suffix}_{user_data.name.replace(' ', '').upper()}"

    existing_user = await admin_user_repository.get_by_mobile_passport(db, user_data)
    if existing_user:
        raise HTTPException(status_code=404, detail="Username already exists")
    return await admin_user_repository.create_admin_user(db, user_data, agency_name, code)

async def admin_user_login(db: AsyncSession, request_credential: OAuth2PasswordRequestForm):
    user = await admin_user_repository.get_admin_user_by_code(db, code=request_credential.username)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password"
        )

    if not verify_password(request_credential.password, user.password):
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password"
        )

    access_token = create_access_token_for_admin_user(
        subject=user.code, role=user.role,
        mobile_no=user.mobile_no, email=user.email,
        code=user.code, agency_name= user.agency_name)
    refresh_token = create_refresh_token_for_admin_user(
        subject=user.code, role=user.role,
        mobile_no=user.mobile_no, email=user.email,
        code=user.code, agency_name= user.agency_name)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }