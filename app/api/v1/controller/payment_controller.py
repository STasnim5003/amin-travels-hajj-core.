import fastapi
from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.controller.pilgrim_controller import public_router
from app.core.middleware.middleware import get_current_user, get_current_admin_user, get_current_pilgrim
from app.service import payment_service, pilgrim_payment_service
from data.db.db_config import get_async_db
from infrastructure.schema.payment_schema import PaymentResponseSchema, PaginatedPaymentResponseForGroupLeader, \
    PaginatedPaymentResponseForAgency, PaymentUpdateSchema, GroupLeaderPayableBaseSchema, PilgrimPayableBaseSchema, \
    PilgrimPaymentBaseSchema, \
    GroupLeaderPaymentBaseSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")


@private_router.post("/group-leader/create-payable", tags=["payment"])
async def create_payable_for_group_leader(
        request: GroupLeaderPayableBaseSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]

    return await payment_service.create_payable_for_group_leader(db, request, agency_name)


@private_router.post("/group-leader/create-payment", response_model=PaymentResponseSchema, tags=["payment"])
async def create_payment_of_group_leader(
        request_schema: GroupLeaderPaymentBaseSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> PaymentResponseSchema:
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user['agency_name']

    return await payment_service.create_group_leader_payment(db, request_schema, agency_name)


@private_router.get("/group-leader/payment-info", response_model=PaginatedPaymentResponseForGroupLeader,
                    tags=["payment"])
async def get_group_leader_payment_info(
        db: AsyncSession = Depends(get_async_db),
        category: str | None = Query(None, description="Filter by payment category"),
        page: int = Query(1, ge=1),
        size: int = Query(100, ge=1),
        current_user: dict = Depends(get_current_admin_user)
):
    if current_user["role"] != "GROUP_LEADER":
        raise HTTPException(status_code=403, detail="Unauthorized")

    group_leader = current_user["code"]

    return await payment_service.get_group_leader_payments(
        db=db,
        group_leader=group_leader,
        category=category,
        page=page,
        size=size
    )


@private_router.get("/agency/payment-info", response_model=PaginatedPaymentResponseForAgency, tags=["payment"])
async def get_agency_payment_info(
        user_type: str = Query("GROUP_LEADER", description="Filter by payment type"),
        db: AsyncSession = Depends(get_async_db),
        category: str | None = Query(None, description="Filter by payment category"),
        group_leader: str | None = Query(None, description="Filter by group leader"),
        tracking_id: str | None = Query(None),
        page: int = Query(1, ge=1),
        size: int = Query(100, ge=1),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")

    agency_name = current_user["agency_name"]

    return await payment_service.get_agency_payments(
        user_type, db, agency_name, group_leader, tracking_id, page, size
    )


@private_router.put("/update-payable/{payable_id}", response_model=PaymentResponseSchema, tags=["payment"])
async def update_payable(
        payable_id: int,
        payable_request: PaymentUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> PaymentResponseSchema:
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    agency_name = current_user["agency_name"]

    return await payment_service.update_payable(db, payable_id, payable_request.dict(exclude_unset=True), agency_name)


@private_router.post("/pilgrim/create-payable", response_model=PaymentResponseSchema, tags=["payment"])
async def create_payable_for_pilgrim(
        request: PilgrimPayableBaseSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> PaymentResponseSchema:
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]

    result = await pilgrim_payment_service.create_payable_for_pilgrim(db, request, agency_name)
    return PaymentResponseSchema.model_validate(result)


@private_router.post("/pilgrim/create-payment", response_model=PaymentResponseSchema, tags=["payment"])
async def create_payment_for_pilgrim(
        request: PilgrimPaymentBaseSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> PaymentResponseSchema:
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]

    return await pilgrim_payment_service.create_payment_for_pilgrim(db, request, agency_name)


@private_router.get("/payment-info/pilgrim", response_model=PaginatedPaymentResponseForGroupLeader, tags=["payment"])
async def get_pilgrim_payment_info(
        db: AsyncSession = Depends(get_async_db),
        category: str | None = Query(None, description="Filter by payment category"),
        page: int = Query(1, ge=1),
        size: int = Query(100, ge=1),
        current_user: dict = Depends(get_current_pilgrim)
):
    tracking_id = current_user.get("tracking_id")
    if not tracking_id:
        raise HTTPException(status_code=400, detail="Tracking ID is missing in user context")

    return await pilgrim_payment_service.get_pilgrim_payments(
        db=db,
        tracking_id=tracking_id,
        category=category,
        page=page,
        size=size
    )

@public_router.get("/payment/{payment_id}", tags=["payment"])
async def get_payment_by_id(
        payment_id: int,
        db: AsyncSession = Depends(get_async_db),
):
    return await payment_service.get_payment_by_id(db,payment_id)

