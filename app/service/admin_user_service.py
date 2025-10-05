from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import admin_user_repository
from infrastructure.schema.admin_user_schema import AdminUserCreate


async def list_users(db: AsyncSession):
    return await admin_user_repository.get_all(db)



async def get_user(db: AsyncSession, user_id: int):
    user = await admin_user_repository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def create_user(db: AsyncSession, user_data: AdminUserCreate, agency_name:str):
    existing_user = await admin_user_repository.get_by_mobile_passport(db, user_data)
    if existing_user:
        raise HTTPException(status_code=404, detail="Username already exists")
    return await admin_user_repository.create_admin_user(db, user_data, agency_name)