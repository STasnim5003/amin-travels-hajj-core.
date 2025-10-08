from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.utils import hash_password
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