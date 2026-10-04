import logging
from typing import Optional, List

import fastapi
from fastapi import Depends, Query, HTTPException, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user, get_current_pilgrim
from app.core.utils.authorize_api import check_agency_or_staff_user, has_required_permissions
from app.service import pilgrim_service
from data.db.db_config import get_async_db
from infrastructure.schema.pilgrim_data_schema import PaginatedPilgrimDataListResponseSchema, \
    BulkUpdatePilgrimRequestSchema, PilgrimLoginResponseSchema, PilgrimDataResponseSchema, PilgrimFamilyGroupAssign, \
    PilgrimReplaceSchema, PilgrimArchiveSchema, ReplacedPilgrimListResponseSchema, \
    PilgrimPreRegistrationEnquire, BookTrainingSession, PilgrimDataBaseSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")

public_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/public")

# who deleted a pilgrim / changed a family code; the rows themselves keep no trace of it
audit_logger = logging.getLogger("pilgrim_audit")


@private_router.get("/pilgrim-data", response_model=PaginatedPilgrimDataListResponseSchema, tags=["Pilgrim"])
async def get_pilgrim_data(
        name_en: Optional[str] = Query(None),
        tracking_id: Optional[str] = Query(None),
        serial_no: Optional[str] = Query(None),
        mobile_no: Optional[str] = Query(None),
        allocation_status: Optional[str] = Query(None),
        registration_status: Optional[str] = Query(None),
        group_leader: Optional[str] = Query(None),
        table_name: Optional[str] = Query(None),
        show_customers: bool = Query(default=True),
        is_package_assigned: bool = Query(None),
        hajj_year: Optional[int] = Query(None),
        family_code: Optional[str] = Query(None),
        group_name: Optional[str] = Query(None),
        sub_group: Optional[str] = Query(None),
        package_name: Optional[str] = Query(None),
        passport_no: Optional[str] = Query(None),
        package_bed_type: Optional[str] = Query(None),
        package_duration: Optional[int] = Query(None),
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1),
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> PaginatedPilgrimDataListResponseSchema:
    extra_filters = dict(family_code=family_code, group_name_filter=group_name, sub_group=sub_group,
                         package_name=package_name, passport_no=passport_no,
                         package_bed_type=package_bed_type, package_duration=package_duration)
    username = current_user.get("username")
    if current_user["role"] == "SUPER_ADMIN":
        return await pilgrim_service.get_pilgrim_data(db, name_en, tracking_id, serial_no, mobile_no, None,
                                                      allocation_status, registration_status, page, size, table_name,
                                                      username, group_leader, show_customers, is_package_assigned,
                                                      hajj_year, **extra_filters)
    else:
        if allocation_status == "UNASSIGNED":
            raise HTTPException(status_code=403, detail="Unauthorized")
        group_name = current_user["agency_name"]
        return await pilgrim_service.get_pilgrim_data(db, name_en, tracking_id, serial_no, mobile_no, group_name,
                                                      allocation_status, registration_status, page,
                                                      size, table_name, username, group_leader, show_customers,
                                                      is_package_assigned, hajj_year, **extra_filters)


@private_router.put("/pilgrim-data", response_model=PaginatedPilgrimDataListResponseSchema, tags=["Pilgrim"])
async def update_pilgrim_data(
        pilgrim_request_schema: BulkUpdatePilgrimRequestSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> PaginatedPilgrimDataListResponseSchema:
    has_required_permissions(current_user=current_user, roles=["SUPER_ADMIN"])

    username = current_user["username"]

    try:
        return await pilgrim_service.update_pilgrim_data_approval_status(db, pilgrim_request_schema, username)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@private_router.put("/pilgrim-data/replace", response_model=PilgrimDataResponseSchema, tags=["Pilgrim"])
async def replace_pilgrim(
        request: PilgrimReplaceSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await pilgrim_service.replace_pilgrim(db=db, request=request, agency_name=agency_name)


@private_router.get("/pilgrim-data/replace", response_model=ReplacedPilgrimListResponseSchema, tags=["Pilgrim"])
async def get_replaced_pilgrims(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await pilgrim_service.get_replaced_pilgrims(db=db, agency_name=agency_name)


@private_router.put("/pilgrim-data/archive", response_model=List[PilgrimDataResponseSchema], tags=["Pilgrim"])
async def archive_pilgrim(
        request: PilgrimArchiveSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")

    agency_name = current_user["agency_name"]
    return await pilgrim_service.archive_pilgrim(db=db, request=request, agency_name=agency_name)


@public_router.post("/pilgrim/login", response_model=PilgrimLoginResponseSchema, tags=["Pilgrim"])
async def pilgrim_login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_async_db)
) -> PilgrimLoginResponseSchema:
    try:
        return await pilgrim_service.pilgrim_login(db, form_data)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@private_router.get("/pilgrim/profile", response_model=PilgrimDataResponseSchema, tags=["Pilgrim"])
async def get_pilgrim_profile(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_pilgrim)
) -> PilgrimDataResponseSchema:
    tracking_id = current_user.get("tracking_id")
    if not tracking_id:
        raise HTTPException(status_code=400, detail="Tracking ID is missing in user context")

    result = await pilgrim_service.get_pilgrim_by_tracking_id(db, tracking_id)

    return PilgrimDataResponseSchema.model_validate(result)


@private_router.put("/pilgrim/register", tags=["Pilgrim"])
async def register_pilgrim(
        vaccination_center: str = Form(...),
        package_id: int = Form(...),
        comment_on_package: Optional[str] = Form(None),
        passport_copy: UploadFile = File(...),
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_pilgrim)
):
    tracking_id = current_user.get("tracking_id")
    # tracking_id = "M30DD883076"
    if not tracking_id:
        raise HTTPException(status_code=400, detail="Tracking ID is missing in user context")
    try:
        return await pilgrim_service.pilgrim_register(db, tracking_id, vaccination_center, passport_copy, package_id,
                                                      comment_on_package)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@private_router.get("/pilgrim/{pilgrim_id}", response_model=PilgrimDataResponseSchema, tags=["Pilgrim"])
async def get_pilgrim_by_id(
        pilgrim_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> PilgrimDataResponseSchema:
    return await pilgrim_service.get_pilgrim_by_id(db, pilgrim_id)


@private_router.put("/pilgrim/assign-family-code", tags=["Pilgrim"])
async def assign_family_code_to_pilgrim(
        request_body: PilgrimFamilyGroupAssign,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    result = await pilgrim_service.assign_family_code(db, request_body, agency_name)
    audit_logger.info(
        "AUDIT family_code %s by user=%s role=%s agency=%s family_code=%s tracking_ids=%s",
        "assign" if request_body.family_code else "remove", current_user.get("username"),
        current_user.get("role"), agency_name, request_body.family_code, request_body.tracking_ids,
    )
    return result


@public_router.post("/pilgrim/pre-register-enquiry", tags=["Pilgrim"])
async def pre_register_enquiry(
        request_body: PilgrimPreRegistrationEnquire,
        db: AsyncSession = Depends(get_async_db)
):
    return await pilgrim_service.pre_register_enquiry(db=db, request_body=request_body)


@public_router.post("/pilgrim/book-training-session", tags=["Pilgrim"])
async def book_hajj_training_session(
        request_body: BookTrainingSession,
        db: AsyncSession = Depends(get_async_db)
):
    return await pilgrim_service.book_training_session(db=db, request_body=request_body)


@private_router.get("/pre-register-enquiry-training-session", tags=["Pilgrim"])
async def get_pre_register_enquiry_training_session_pilgrims(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    agency_name = current_user["agency_name"]
    return await pilgrim_service.get_pre_register_enquiry_training_session_pilgrims(db=db, agency_name=agency_name)

@private_router.get("/pilgrim-agreement/{family_code}", tags=["Pilgrim"])
async def get_pilgrim_agreement_by_family_code(
        family_code: str,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await pilgrim_service.get_pilgrim_agreement_by_family_code(db=db, family_code=family_code, agency_name=agency_name)

@private_router.post("/pilgrim/pre-registration", tags=["Pilgrim"])
async def manual_pre_registration(
        request: PilgrimDataBaseSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    username = current_user["username"]
    return await pilgrim_service.manual_pre_registration(db=db, agency_name=agency_name, username=username, request=request)

@private_router.delete("/pilgrim/{tracking_id}", tags=["Pilgrim"])
async def delete_pilgrim(
        tracking_id: str,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    result = await pilgrim_service.delete_pilgrim(db=db, tracking_id=tracking_id, agency_name=agency_name)
    audit_logger.info(
        "AUDIT pilgrim delete by user=%s role=%s agency=%s tracking_id=%s",
        current_user.get("username"), current_user.get("role"), agency_name, tracking_id,
    )
    return result