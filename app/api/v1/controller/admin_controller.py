from typing import Optional

import fastapi
from fastapi import Depends, Form, UploadFile, File, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.core.middleware.middleware import get_current_user
from app.core.utils.authorize_api import has_required_permissions, check_agency_or_staff_user, STAFF_ROLES
from app.service import admin_service
from data.db.db_config import get_async_db
from infrastructure.schema.admin_schema import AdminResponseSchema, AdminListResponseSchema, \
    AdminProfileUpdateResponseSchema, AssignLeadAgencySchema, CheckLeadAssignResponseSchema, \
    SubAgencyAmountUpdateSchema

router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/public")
private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")


@private_router.post("/admin", response_model=AdminResponseSchema, tags=["admin"])
async def create_admin_endpoint(
        db: AsyncSession = Depends(get_async_db),
        user_name: str = Form(...),
        password: str = Form(...),
        role: str = Form(...),
        agency_name: str = Form(...),
        license_number: str = Form(...),
        mobile_no: str = Form(...),
        email: Optional[str] = Form(...),
        current_user: dict = Depends(get_current_user)

):
    has_required_permissions(current_user=current_user, roles=['SUPER_ADMIN'])
    response = await admin_service.create_admin(
        db=db,
        user_name=user_name,
        password=password,
        role=role,
        agency_name=agency_name,
        license_number=license_number,
        mobile_no=mobile_no,
        email=email
    )
    return JSONResponse(content=jsonable_encoder(response))


@private_router.get("/admin", response_model=AdminListResponseSchema, tags=["admin"])
async def get_all_admins(
        page: int = Query(1, ge=1),
        limit: int = Query(100, ge=1),
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    has_required_permissions(current_user=current_user, roles=["SUPER_ADMIN", "AGENCY", *STAFF_ROLES])
    return await admin_service.get_all_admins(db=db, page=page, limit=limit)


@private_router.get("/admin/profile", response_model=AdminResponseSchema, tags=["admin"])
async def get_admin_profile(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> AdminResponseSchema:
    username = current_user["username"]
    agency_name = current_user['agency_name']
    return await admin_service.get_admin_profile(db=db, username=username, agency_name=agency_name)


@private_router.get("/admin/{admin_id}", response_model=AdminResponseSchema, tags=["admin"])
async def get_admin_by_id(
        admin_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> AdminResponseSchema:
    has_required_permissions(current_user=current_user, roles=['SUPER_ADMIN'])
    return await admin_service.get_admin_by_id(db, admin_id)


@private_router.delete("/admin/{admin_id}", response_model=AdminProfileUpdateResponseSchema, tags=["admin"])
async def delete_admin_by_id(
        admin_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> AdminProfileUpdateResponseSchema:
    has_required_permissions(current_user=current_user, roles=['SUPER_ADMIN'])

    return await admin_service.delete_admin_by_id(db, admin_id)


@private_router.put("/admin/profile", response_model=AdminResponseSchema, tags=["admin"])
async def update_admin_profile(
        location: str = Form(None),
        google_map_location: str = Form(None),
        logo: UploadFile = File(None),
        passport_copy: UploadFile = File(None),
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> AdminResponseSchema:
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await admin_service.update_admin_profile(db, location, google_map_location, logo, passport_copy,
                                                    agency_name)


@private_router.put("/admin/assign-lead-agency", tags=["admin"])
async def assign_lead_agency(
        request: AssignLeadAgencySchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    user_role = current_user["role"]
    has_required_permissions(current_user=current_user, roles=["SUPER_ADMIN", "AGENCY", *STAFF_ROLES])

    request_dict = request.model_dump()
    if user_role == "SUPER_ADMIN":
        if not request_dict['agency_name'] or not request_dict['lead_agency_name']:
            raise HTTPException(status_code=400, detail="Give Agency Names")

    if user_role == "AGENCY":
        agency_name = current_user["agency_name"]
        if request_dict['agency_name'] and request_dict['agency_name'] != agency_name:
            raise HTTPException(status_code=400, detail="Agency name mismatched")

        request_dict["agency_name"] = agency_name
    return await admin_service.assign_lead_agency(db, request_dict)


@private_router.get("/lead-agency/pilgrims", tags=["admin"])
async def get_lead_agency_pilgrims(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    has_required_permissions(current_user=current_user, roles=["SUPER_ADMIN", "AGENCY", *STAFF_ROLES])

    lead_agency_name = current_user["agency_name"]
    return await admin_service.get_lead_agency_pilgrims(db, lead_agency_name)


@private_router.get("/lead-agency-assignment-check", tags=["admin"])
async def get_lead_agency_assignment_check(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    has_required_permissions(current_user=current_user, roles=["SUPER_ADMIN", "AGENCY", *STAFF_ROLES])

    agency_name = current_user["agency_name"]
    result = await admin_service.check_lead_agency_assignment(db, agency_name)
    return CheckLeadAssignResponseSchema.model_validate(result)


@private_router.get("/sub-agencies", tags=["admin"])
async def get_sub_agencies(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await admin_service.get_sub_agencies_with_amount(db, agency_name)


@private_router.get("/agency-amount", tags=["admin"])
async def get_agency_amount(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await admin_service.get_agency_amount(db, agency_name)


@private_router.put("/sub-agencies/update-amount", tags=["admin"])
async def update_sub_agency_amount(
        sub_agency_account_update: SubAgencyAmountUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await admin_service.update_sub_agency_amount(db, agency_name, sub_agency_account_update)
