from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import file_repository


async def upload_file(name:str, file: UploadFile):
    try:

        result = await file_repository.upload_file(name=name,file=file)
        return result
    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))



async def check_download_access(db: AsyncSession, current: dict, key: str):
    """Pilgrims may only fetch files on their own records. Staff may fetch any file except one
    held by another agency's records. SUPER_ADMIN is unrestricted."""
    object_key = file_repository.get_object_key(key)
    if not current.get("username"):
        if not await file_repository.is_pilgrim_file(db, current["tracking_id"], object_key):
            raise HTTPException(status_code=403, detail="Not allowed to access this file")
        return
    if current.get("role") == "SUPER_ADMIN":
        return
    owners = await file_repository.get_file_agencies(db, object_key)
    if owners and (current.get("agency_name") or "").strip().lower() not in owners:
        raise HTTPException(status_code=403, detail="Not allowed to access this file")


async def get_download_url(db: AsyncSession, current: dict, key: str):
    await check_download_access(db, current, key)
    try:
        result = await file_repository.get_download_url(key)
        return result
    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


async def update_file(key, new_file:UploadFile):
    try:
        result = await file_repository.update_file(key, new_file)
        return result
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


async def delete_file(key):
    try:
        result = await file_repository.delete_file(key)
        return result
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))