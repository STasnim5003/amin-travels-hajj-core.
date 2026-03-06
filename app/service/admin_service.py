from typing import Optional

from fastapi import HTTPException, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.utils.file_downloadable_url import generate_downloadable_urls
from app.core.utils.get_current_time import get_current_time
from app.core.utils.utils import hash_password, verify_password, create_access_token, create_refresh_token
from data.repository import admin_repository, file_repository
from infrastructure.schema.admin_schema import AdminBaseSchema, AdminResponseSchema, AdminListResponseSchema, \
    AdminProfileUpdateResponseSchema, SubAgencyAmountUpdateSchema, LogoUpdateSchema


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
        db: AsyncSession,
        location: str,
        google_map_location: str,
        logo: UploadFile,
        passport_copy: UploadFile,
        agency_name: str
):
    logo_data = []
    if logo:
        try:
            logo_resp = await file_repository.upload_file(file=logo, name="logo")
            logo_data.append(logo_resp.model_dump())

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    passport_data = []
    if passport_copy:
        try:
            passport_resp = await file_repository.upload_file(file=passport_copy, name="passport")
            passport_data.append(passport_resp.model_dump())
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    try:
        response = await admin_repository.update_admin_profile(db, location, google_map_location, logo_data,
                                                               passport_data, agency_name)
        if response.passport_copy:
            response.passport_copy = await generate_downloadable_urls(response.passport_copy)
        if response.logo:
            response.logo = await generate_downloadable_urls(response.logo)
        return response

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def assign_lead_agency(db: AsyncSession, request: dict):
    try:

        fetched_agency = await admin_repository.get_agency_by_agency_name(db, request['agency_name'])
        lead_agency = await admin_repository.get_agency_by_agency_name(db, request['lead_agency_name'])

        if not fetched_agency or not lead_agency:
            raise HTTPException(status_code=400, detail="Agency Not found")

        result = await admin_repository.assign_lead_agency(db, request)
        if result:
            return {"message": "Lead agency assigned successfully"}
    except Exception as e:
        raise e


async def get_lead_agency_pilgrims(db: AsyncSession, lead_agency_name: str):
    try:
        records = await admin_repository.get_lead_agency_pilgrims(db, lead_agency_name)

        agencies = []
        for row in records:
            agencies.append({
                "agency_name": row["agency_name"],
                "total_pilgrims": row["total_pilgrims"],
                "name_en": None,
                "tracking_id": None,
                "serial_no": None,
                "voucher": None,
                "mobile_no": None,
                "passport_no": None,
                "passport_expiry_date": None,
                "date_of_birth": None,
                "nid": None,
                "gender": None,
                "passport_dob": None,
                "passport_type": None,
                "pilgrims": row["pilgrims"]
            })

        return {
            "lead_agency_name": lead_agency_name,
            "agencies": agencies
        }
    except Exception as e:
        raise e


async def check_lead_agency_assignment(db, agency_name):
    try:
        result = await admin_repository.check_lead_agency_assignment(db, agency_name)
        return {
            "agency_name": agency_name,
            "lead_agency_name": result
        }
    except Exception as e:
        raise e


async def get_child_agencies(db: AsyncSession, lead_agency_name: str):
    try:
        agencies = await admin_repository.get_child_agencies(db, lead_agency_name)
        return agencies
    except Exception as e:
        raise e


async def update_sub_agency_amount(db: AsyncSession, agency_name: str,
                                   sub_agency_account_update: SubAgencyAmountUpdateSchema):
    try:
        agencies = await admin_repository.get_child_agencies(db, agency_name)
        if sub_agency_account_update.agency_name not in agencies:
            raise HTTPException(status_code=400, detail="It is not your sub agency")

        request_schema = sub_agency_account_update.model_dump()
        request_schema["updated_by"] = agency_name
        request_schema["updated_at"] = get_current_time()

        return await admin_repository.update_sub_agency_amount(db, request_schema)
    except Exception as e:
        raise e


async def get_sub_agencies_with_amount(db, agency_name):
    try:
        agencies = await admin_repository.get_sub_agencies_with_amount(db, agency_name)
        return agencies
    except Exception as e:
        raise e


async def get_agency_amount(db:AsyncSession, agency_name:str):
    try:
        agency_amount = await admin_repository.get_agency_amount(db, agency_name)
        return agency_amount
    except Exception as e:
        raise e


async def update_logo(db:AsyncSession, request:LogoUpdateSchema, agency_name:str, username:str):
    try:
        request_dict = request.model_dump(exclude_none=True)
        request_dict['agency_name'] = agency_name
        request_dict['updated_by'] = username
        request_dict['updated_at'] = get_current_time()

        await admin_repository.update_log(db=db, request_dict=request_dict)
        return True
    except Exception as e:
        raise e