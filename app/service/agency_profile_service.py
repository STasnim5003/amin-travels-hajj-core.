from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.file_downloadable_url import generate_downloadable_urls
from data.repository import admin_user_repository
from infrastructure.schema.admin_schema import AdminResponseSchema


async def get_agency_profile(db: AsyncSession, username: str, agency_name: str) -> AdminResponseSchema:
    try:
        admin = await admin_user_repository.get_admin_profile(db=db, username=username, agency_name=agency_name)
        if not admin:
            raise HTTPException(status_code=404, detail="Agency profile not found")

        if admin['passport_copy']:
            admin['passport_copy'] = await generate_downloadable_urls(admin['passport_copy'])
        if admin['logo']:
            admin['logo'] = await generate_downloadable_urls(admin['logo'])

        return AdminResponseSchema.model_validate(admin)
    except Exception as e:
        raise e
