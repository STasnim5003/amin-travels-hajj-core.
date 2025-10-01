from typing import Optional

from fastapi import HTTPException, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.utils.file_downloadable_url import generate_downloadable_urls
from app.core.utils.utils import hash_password, verify_password, create_access_token, create_refresh_token
from data.repository import admin_repository, file_repository
from infrastructure.schema.admin_schema import AdminBaseSchema, AdminResponseSchema, AdminListResponseSchema, \
    AdminProfileUpdateResponseSchema


async def create_admin(db: AsyncSession,
                       user_name: str,
                       password: str,
                       role: str,
                       agency_name: str,
                       license_number: str,
                       mobile_no: str,
                       email: Optional[str],
                       ) -> AdminResponseSchema:
    hashed_password = hash_password(password)

    new_admin = AdminBaseSchema(
        user_name=user_name,
        password=hashed_password,
        role=role,
        agency_name=agency_name,
        license_number=license_number,
        mobile_no=mobile_no,
        email=email,
        is_active=True,

    )
    try:
        response = await admin_repository.insert_admin(new_admin, db=db)
        # if response.passport_copy:
        #     response.passport_copy = await generate_downloadable_urls(response.passport_copy)
        # if response.logo:
        #     response.logo = await generate_downloadable_urls(response.logo)
        return response

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def admin_login(db: AsyncSession, request_credential: OAuth2PasswordRequestForm):
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


async def get_all_admins(db: AsyncSession, page: int, limit: int) -> AdminListResponseSchema:
    offset = (page - 1) * limit
    try:
        admins, total = await admin_repository.get_all_admin(db, offset=offset, limit=limit)
        return AdminListResponseSchema(
            data=admins,
            total=total,
            page=page,
            size=limit
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        raise HTTPException(status_code=500, detail="Error occurred while retrieving admin data.")


async def get_admin_by_id(db: AsyncSession, admin_id: int) -> AdminResponseSchema:
    try:
        admin = await admin_repository.get_admin_by_id(db, admin_id=admin_id)
        if admin.passport_copy:
            admin.passport_copy = await generate_downloadable_urls(admin.passport_copy)
        if admin.logo:
            admin.logo = await generate_downloadable_urls(admin.logo)
        return AdminResponseSchema.model_validate(admin)
    except HTTPException as http_exc:
        raise http_exc

    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected error occurred while fetching the admin.")


async def get_admin_by_username(db: AsyncSession, username: str) -> AdminResponseSchema:
    try:
        admin = await admin_repository.get_admin_by_username(db, username=username)
        if admin.passport_copy:
            admin.passport_copy = await generate_downloadable_urls(admin.passport_copy)
        if admin.logo:
            admin.logo = await generate_downloadable_urls(admin.logo)

        return AdminResponseSchema.model_validate(admin)
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected error occurred while fetching the admin.")


async def delete_admin_by_id(db: AsyncSession, admin_id: int) -> AdminProfileUpdateResponseSchema:
    try:
        message = await admin_repository.delete_admin_by_id(db, admin_id=admin_id)
        return AdminProfileUpdateResponseSchema(
            message=message["message"],
            status=204
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error occurred while deleting the admin.")

async def update_admin_profile(
        db:AsyncSession,
        location: str,
        google_map_location: str,
        logo: UploadFile,
        passport_copy: UploadFile,
        agency_name: str
):
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


    try:
        response = await admin_repository.update_admin_profile(db, location, google_map_location, logo_data, passport_data, agency_name )
        if response.passport_copy:
            response.passport_copy = await generate_downloadable_urls(response.passport_copy)
        if response.logo:
            response.logo = await generate_downloadable_urls(response.logo)
        return response

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

