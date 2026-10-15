from fastapi import HTTPException, UploadFile

from data.repository import file_repository


async def upload_file(name:str, file: UploadFile):
    try:

        result = await file_repository.upload_file(name=name,file=file)
        return result
    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))



async def get_download_url(key):
    try:
        result = await file_repository.get_download_url(key)
        return result
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