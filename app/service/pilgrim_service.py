from os import access
from pyexpat.errors import messages
from typing import Optional

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import UploadFile

from app.core.utils.file_downloadable_url import generate_downloadable_urls
from app.core.utils.utils import verify_pilgrim_password, create_access_token_for_pilgrim, \
    create_refresh_token_for_pilgrim
from app.service import view_field_service
from data.repository import pilgrim_repository, file_repository
from data.repository.pilgrim_repository import fetch_pilgrim_data_json
from infrastructure.schema.pilgrim_data_schema import PaginatedPilgrimDataListResponseSchema, \
    BulkUpdatePilgrimRequestSchema, PilgrimLoginResponseSchema, PilgrimDataResponseSchema, \
    PilgrimRegistrationRequestSchema, PilgrimFamilyGroupAssign


async def get_pilgrim_data(db: AsyncSession,
                           name_en: Optional[str],
                           tracking_id: Optional[str],
                           serial_no: Optional[str],
                           mobile_no: Optional[str],
                           group_name: Optional[str],
                           allocation_status: Optional[str],
                           registration_status: Optional[str],
                           page: int, limit: int,
                           table_name: Optional[str],
                           username: Optional[str],
                           group_leader: Optional[str],
                           ) -> PaginatedPilgrimDataListResponseSchema:
    skip = (page - 1) * limit

    pilgrims, total, registration_status_count, allocation_status_count = await fetch_pilgrim_data_json(db, name_en,
                                                                                                        tracking_id,
                                                                                                        serial_no,
                                                                                                        mobile_no,
                                                                                                        group_name,
                                                                                                        allocation_status,
                                                                                                        registration_status,
                                                                                                        group_leader,
                                                                                                        skip, limit)
    views = []
    if username:
        views = await view_field_service.get_views(db, username)

    counts = registration_status_count or allocation_status_count or {}

    return PaginatedPilgrimDataListResponseSchema(
        data=pilgrims,
        total=total,
        page=page,
        size=limit,
        views=views,
        counts=counts
    )


async def update_pilgrim_data_approval_status(db: AsyncSession, data: BulkUpdatePilgrimRequestSchema, username: str):
    try:
        response = await pilgrim_repository.update_pilgrim_approval_status(data=data, db=db, username=username)

        return PaginatedPilgrimDataListResponseSchema(
            data=response,
            total=len(response),
            page=1,
            size=len(response)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def pilgrim_login(db: AsyncSession, request_credentials: OAuth2PasswordRequestForm):
    try:
        pilgrim = await pilgrim_repository.get_pilgrim_by_tracking_id(db, request_credentials.username)

        if not pilgrim:
            raise HTTPException(status_code=404, detail="Incorrect Tracking Id or Password.")

        is_password_matched = verify_pilgrim_password(request_credentials.password, pilgrim.password)
        if not is_password_matched:
            raise HTTPException(status_code=404, detail="Incorrect Tracking Id or Password.")

        access_token = create_access_token_for_pilgrim(subject=pilgrim.name_en, mobile_no=pilgrim.mobile_no,
                                                       tracking_id=pilgrim.tracking_id)
        refresh_token = create_refresh_token_for_pilgrim(subject=pilgrim.name_en, mobile_no=pilgrim.mobile_no,
                                                         tracking_id=pilgrim.tracking_id)

        return PilgrimLoginResponseSchema(
            access_token=access_token,
            refresh_token=refresh_token
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def get_pilgrim_by_tracking_id(db: AsyncSession, tracking_id: str):
    pilgrim = await pilgrim_repository.get_pilgrim_by_tracking_id(db, tracking_id)
    passport_copy = pilgrim.passport_copy
    response = dict(pilgrim._mapping)
    if passport_copy:
        passport_copy_with_download = await generate_downloadable_urls(passport_copy)
        response["passport_copy"] = passport_copy_with_download
    return response


async def pilgrim_register(db: AsyncSession, tracking_id: str, vaccination_center: str,
                           passport_copy: UploadFile, package_id: int, comment_on_package: str):
    passport_data = []
    try:
        passport_resp = await file_repository.upload_file(file=passport_copy, name="passport")
        passport_data.append(passport_resp.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    new_pilgrim_registration_request = PilgrimRegistrationRequestSchema(
        vaccination_center=vaccination_center,
        passport_copy=passport_data,
        tracking_id=tracking_id,
        package_id=package_id,
        comment_on_package=comment_on_package
    )

    try:
        pilgrim =  await pilgrim_repository.pilgrim_register(db, new_pilgrim_registration_request)
        pilgrim_dict = pilgrim.__dict__.copy()
        if pilgrim_dict.get("passport_copy"):
            passport_data_urls = await generate_downloadable_urls(passport_data)
            pilgrim_dict["passport_copy"] = passport_data_urls

        return PilgrimDataResponseSchema.model_validate(pilgrim_dict)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def get_pilgrim_by_id(db: AsyncSession, pilgrim_id: int) -> PilgrimDataResponseSchema:
    try:
        pilgrim = await pilgrim_repository.get_pilgrim_by_id(db, pilgrim_id)

        if not pilgrim:
            raise HTTPException(status_code=400, detail="Pilgrim not found.")
        pilgrim_dict = pilgrim.__dict__.copy()  # convert model to dict
        if pilgrim_dict.get("passport_copy"):
            pilgrim_dict["passport_copy"] = await generate_downloadable_urls(pilgrim_dict["passport_copy"])

        return PilgrimDataResponseSchema.model_validate(pilgrim_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def assign_family_code(db:AsyncSession, request_body:PilgrimFamilyGroupAssign, agency_name:str):
    pilgrims = await pilgrim_repository.get_pilgrims_by_tracking_ids(db, request_body.tracking_ids)
    family_codes = await pilgrim_repository.available_family_codes(db)

    if not pilgrims:
        raise HTTPException(status_code=400, detail="No pilgrims found.")

    if request_body.family_code in family_codes:
        raise HTTPException(status_code=400, detail="Family code already exists.")

    for pilgrim in pilgrims:
        if pilgrim.group_name != agency_name:
            raise HTTPException(status_code=400, detail="Pilgrim group name does not match.")


    result = await pilgrim_repository.assign_family_code(db, request_body)
    return [PilgrimDataResponseSchema.model_validate(r) for r in result]