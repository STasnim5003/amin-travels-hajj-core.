from typing import Optional

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import UploadFile

from app.core.utils.data_clean import generate_password
from app.core.utils.file_downloadable_url import generate_downloadable_urls
from app.core.utils.get_current_time import get_current_time
from app.core.utils.utils import verify_pilgrim_password, create_access_token_for_pilgrim, \
    create_refresh_token_for_pilgrim, hash_password
from app.service import view_field_service
from data.repository import pilgrim_repository, file_repository
from data.repository.pilgrim_repository import fetch_pilgrim_data_json
from infrastructure.schema.pilgrim_data_schema import PaginatedPilgrimDataListResponseSchema, \
    BulkUpdatePilgrimRequestSchema, PilgrimLoginResponseSchema, PilgrimDataResponseSchema, \
    PilgrimRegistrationRequestSchema, PilgrimFamilyGroupAssign, PilgrimReplaceSchema, \
    PilgrimArchiveSchema, ReplacedPilgrimResponseSchema, ReplacedPilgrimListResponseSchema, \
    PilgrimPreRegistrationEnquire, PreRegistrationOrBookTrainingResponse, BookTrainingSession, PilgrimDataBaseSchema


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
                           show_customers: bool,
                           is_package_assigned: Optional[bool],
                           hajj_year: Optional[int],
                           family_code: Optional[str] = None,
                           group_name_filter: Optional[str] = None,
                           sub_group: Optional[str] = None,
                           package_name: Optional[str] = None,
                           passport_no: Optional[str] = None,
                           package_bed_type: Optional[str] = None,
                           package_duration: Optional[int] = None,
                           is_nrb: Optional[bool] = None,
                           ) -> PaginatedPilgrimDataListResponseSchema:
    skip = (page - 1) * limit
    try:

        pilgrims, total, registration_status_count, allocation_status_count = await fetch_pilgrim_data_json(db, name_en,
                                                                                                            tracking_id,
                                                                                                            serial_no,
                                                                                                            mobile_no,
                                                                                                            group_name,
                                                                                                            allocation_status,
                                                                                                            registration_status,
                                                                                                            group_leader,
                                                                                                            show_customers,
                                                                                                            is_package_assigned,
                                                                                                            hajj_year,
                                                                                                            skip, limit,
                                                                                                            family_code,
                                                                                                            group_name_filter,
                                                                                                            sub_group,
                                                                                                            package_name,
                                                                                                            passport_no,
                                                                                                            package_bed_type,
                                                                                                            package_duration,
                                                                                                            is_nrb)
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
    except Exception as e:
        raise e


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
        pilgrim = await pilgrim_repository.pilgrim_register(db, new_pilgrim_registration_request)
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


async def assign_family_code(db: AsyncSession, request_body: PilgrimFamilyGroupAssign, agency_name: str):
    pilgrims = await pilgrim_repository.get_pilgrims_by_tracking_ids(db, request_body.tracking_ids)

    if not pilgrims:
        raise HTTPException(status_code=400, detail="No pilgrims found.")

    for pilgrim in pilgrims:
        if pilgrim.group_name != agency_name:
            raise HTTPException(status_code=400, detail="Pilgrim group name does not match.")
        if pilgrim.hajj_year != request_body.hajj_year:
            raise HTTPException(status_code=400, detail="All selected pilgrims must belong to the same Hajj year.")

    if request_body.family_code is not None:
        is_family_code_taken_by_others = await pilgrim_repository.is_family_codes_available(
            db, request_body.family_code, request_body.hajj_year, exclude_tracking_ids=request_body.tracking_ids
        )

        if is_family_code_taken_by_others:
            raise HTTPException(status_code=400, detail="Family code already exists.")

    result = await pilgrim_repository.assign_family_code(db, request_body)
    return [PilgrimDataResponseSchema.model_validate(r) for r in result]


async def replace_pilgrim(db: AsyncSession, request: PilgrimReplaceSchema, agency_name: str):
    try:
        pilgrim = await pilgrim_repository.get_pilgrim_by_id(db=db, pilgrim_id=request.id)

        if pilgrim.group_name != agency_name:
            raise HTTPException(status_code=400, detail="Pilgrim group name does not match.")

        request_dict = request.model_dump(exclude={"id"})

        request_dict.update({
            "total_payment": 0,
            "total_payable": 0,
            "total_due": 0,
            "total_available_amount": 0,
            "package_price_discount": 0,
            "actual_payable": 0,
            "is_package_assigned": False,
            "allocation_status": "ASSIGNED",
            "registration_status": "REGISTERED",
            "preliminary_password": pilgrim.preliminary_password,
            "password": pilgrim.password,
            "is_assigned": True,
            "created_by": agency_name,
            "updated_by": agency_name,
            "group_name": agency_name,
            "created_at": get_current_time(),
            "updated_at": get_current_time(),
        })

        replaced_dict = {
            "id": request.id,
            "registration_status": "REPLACED"
        }

        replaced_details_dict = {
            "tracking_id": request.tracking_id,
            "name_en": request.name_en,
            "replaced_tracking_id": pilgrim.tracking_id,
            "replaced_name_en": pilgrim.name_en,
            "agency_name": agency_name,
            "created_by": agency_name,
            "updated_by": agency_name
        }

        result = await pilgrim_repository.replace_pilgrim(db=db, request_dict=request_dict, replaced_dict=replaced_dict,
                                                          replaced_details_dict=replaced_details_dict)
        return PilgrimDataResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def archive_pilgrim(db: AsyncSession, request: PilgrimArchiveSchema, agency_name: str):
    try:
        pilgrims = await pilgrim_repository.get_pilgrims_by_tracking_ids(db, request.tracking_ids)

        if not pilgrims:
            raise HTTPException(status_code=400, detail="No pilgrims found.")

        update_data = request.model_dump(exclude={"tracking_ids"})

        update_data["updated_by"] = agency_name
        update_data["updated_at"] = get_current_time()

        updated_pilgrims = await pilgrim_repository.archive_pilgrims(
            db,
            tracking_ids=request.tracking_ids,
            update_data=update_data
        )
        return [PilgrimDataResponseSchema.model_validate(r) for r in updated_pilgrims]
    except Exception as e:
        raise e


async def get_replaced_pilgrims(db, agency_name):
    try:
        replaced_pilgrims = await pilgrim_repository.get_replaced_pilgrims(db, agency_name)
        return ReplacedPilgrimListResponseSchema(
            replaced_pilgrims=[
                ReplacedPilgrimResponseSchema.model_validate(r)
                for r in replaced_pilgrims
            ]
        )
    except Exception as e:
        raise e


async def pre_register_enquiry(db: AsyncSession, request_body: PilgrimPreRegistrationEnquire):
    try:
        request_dict = request_body.model_dump()
        request_dict["agency_name"] = "Amin Travels & Tours"
        request_dict["purpose"] = "Pre-Register"
        request_dict["created_by"] = "pilgrim"
        request_dict["updated_by"] = "pilgrim"

        pilgrim = await pilgrim_repository.pre_register_enquiry_or_book_training_session(db=db,
                                                                                         request_dict=request_dict)
        return PreRegistrationOrBookTrainingResponse.model_validate(pilgrim)
    except Exception as e:
        raise e


async def book_training_session(db: AsyncSession, request_body: BookTrainingSession):
    try:
        request_dict = request_body.model_dump()
        request_dict["agency_name"] = "Amin Travels & Tours"
        request_dict["purpose"] = "Training Session"
        request_dict["created_by"] = "pilgrim"
        request_dict["updated_by"] = "pilgrim"

        pilgrim = await pilgrim_repository.pre_register_enquiry_or_book_training_session(db=db,
                                                                                         request_dict=request_dict)
        return PreRegistrationOrBookTrainingResponse.model_validate(pilgrim)
    except Exception as e:
        raise e


async def get_pre_register_enquiry_training_session_pilgrims(db: AsyncSession, agency_name: str):
    try:
        pilgrims = await pilgrim_repository.get_pre_register_enquiry_training_session_pilgrims(db=db,
                                                                                               agency_name=agency_name)
        return [PreRegistrationOrBookTrainingResponse.model_validate(pilgrim) for pilgrim in pilgrims]
    except Exception as e:
        raise e


async def get_pilgrim_agreement_by_family_code(
    db: AsyncSession,
    family_code: str,
    agency_name: str,
):
    result = await pilgrim_repository.get_pilgrim_agreement_by_family_code(
        db=db,
        family_code=family_code,
        agency_name=agency_name,
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Pilgrim agreement not found.",
        )

    return result


async def manual_pre_registration(db:AsyncSession, agency_name:str, username:str, request:PilgrimDataBaseSchema):
    try:
        preliminary_password = generate_password()
        hashed_password = hash_password(preliminary_password)
        request_dict = request.model_dump(exclude_none=True)
        request_dict.update({
            'group_name':agency_name,
            'is_assigned': True,
            'allocation_status': 'ASSIGNED',
            'registration_status': "PREREGISTERED",
            'is_package_assigned': False,
            'created_by': username,
            'updated_by': username,
            'is_active': True,
            'preliminary_password': preliminary_password,
            'password':hashed_password
        })

        result = await pilgrim_repository.manual_pre_registration(db=db, request_dict=request_dict)
        return PilgrimDataResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def delete_pilgrim(db:AsyncSession, tracking_id:str, agency_name:str):
    try:
        pilgrim = await pilgrim_repository.get_pilgrim_by_tracking_id(db, tracking_id)
        if not pilgrim:
            raise HTTPException(status_code=404, detail="Pilgrim not found.")
        if pilgrim.group_name != agency_name:
            raise HTTPException(status_code=400, detail="Pilgrim group name does not match.")
        # deleting would orphan the pilgrim's payments / package bill; family codes can be changed in place
        if pilgrim.is_package_assigned or await pilgrim_repository.has_payments(db, tracking_id):
            raise HTTPException(
                status_code=400,
                detail="Pilgrim has payments or an assigned package and cannot be deleted. "
                       "To change the family code, use Remove Family Code / Assign Family Code instead.",
            )
        await pilgrim_repository.delete_pilgrim(db, tracking_id)
        return {"message": "Pilgrim deleted successfully."}
    except Exception as e:
        raise e
