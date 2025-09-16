from typing import Optional

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.datastructures import UploadFile

from app.core.utils.utils import hash_password, verify_password, create_access_token, create_refresh_token
from data.repository import admin_repository, file_repository
from infrastructure.schema.admin_schema import AdminBaseSchema, AdminResponseSchema


async def create_admin(db: AsyncSession,
                       user_name: str,
                       password: str,
                       role: str,
                       agency_name: str,
                       license_number : str,
                       mobile_no: str,
                       location: Optional[str],
                       email : Optional[str],
                       logo: UploadFile,
                       passport_copy: UploadFile) -> AdminResponseSchema:

    hashed_password = hash_password(password)

    logo_data = []
    try:
        logo_resp = await file_repository.upload_file(file=logo, name="logo")
        logo_data.append(logo_resp.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    passport_data = []
    try:
        passport_resp = await file_repository.upload_file(file=passport_copy, name="passport")
        passport_data.append(passport_resp.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    new_admin = AdminBaseSchema(
        user_name= user_name,
        password=hashed_password,
        role=role,
        agency_name=agency_name,
        license_number=license_number,
        mobile_no=mobile_no,
        location=location,
        email=email,
        logo=logo_data,
        passport_copy=passport_data,
        is_active =True,

    )
    try:
        return await admin_repository.insert_admin(new_admin, db=db)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


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

    access_token = create_access_token(subject=user.user_name, role=user.role, agency_name=user.agency_name)
    refresh_token = create_refresh_token(subject=user.user_name, role=user.role, agency_name=user.agency_name)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }