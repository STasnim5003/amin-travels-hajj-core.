from typing import List

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.datastructures import UploadFile

from app.core.utils import utils
from data.repository import user_repository, file_repository
from infrastructure.schema.user_schema import UserBaseSchema, UserResponseSchema
from app.core.utils.utils import hash_password, verify_password, create_access_token, create_refresh_token


async def create_user(user_request_schema: UserBaseSchema, db: AsyncSession, nid:List[UploadFile]) -> UserResponseSchema:
    nid_images = []
    for pic in nid:
       nid_images.append(await file_repository.upload_file(file=pic, name="users"))

    user_request_schema.nid_images = nid_images
    result = await user_repository.insert_user(user_request_schema, db=db)
    return result


async def get_users( db: AsyncSession, name:str=None, whats_app_no: str=None,page:int=0, limit:int=10, search: str=None) -> List[UserResponseSchema]:
    result = await user_repository.get_users(name=name, whats_app_no=whats_app_no,search=search, page=page,limit=limit,db=db)
    return result


async def update_user(id, payment_status, db):
    result = await user_repository.update_user(id=id, payment_status=payment_status, db=db)
    return result


async def create_credentials(password ,db):
    # random_pass = utils.generate_password()
    result = await user_repository.create_credentials( password=hash_password(password), db=db)
    return result


async def user_login(request_credential: OAuth2PasswordRequestForm, db: AsyncSession):
    user = await user_repository.get_user_by_username(username=request_credential.username, db=db)
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

    access_token = create_access_token(subject=user.username, role=user.role)
    refresh_token = create_refresh_token(subject=user.username, role=user.role)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }