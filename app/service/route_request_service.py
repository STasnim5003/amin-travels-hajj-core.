from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from app.service import admin_service
from data.repository import route_request_repository, admin_repository
from infrastructure.schema.route_request_schema import RouteRequestBaseSchema, RouteRequestResponseSchema, \
    RouteRequestListResponseSchema, RouteRequestUpdateSchema


async def validate_mashaer_pax(
        db: AsyncSession,
        agency_name: str,
        new_pax: int,
):
    arrival_hajji = await route_request_repository.find_hajji_by_route_type(
        db=db,
        route_type="ARRIVAL",
        agency_name=agency_name,
    )

    mashaer_hajji = await route_request_repository.find_hajji_by_route_type(
        db=db,
        route_type="MASHAER",
        agency_name=agency_name,
    )

    total_arrival = sum(a.number_of_pax for a in arrival_hajji)
    total_mashaer = sum(m.number_of_pax for m in mashaer_hajji)

    if len(mashaer_hajji) == 0:
        if total_mashaer + new_pax > total_arrival:
            raise HTTPException(
                status_code=400,
                detail="Mashaer pax must be equal arrival pax",
            )

    elif len(mashaer_hajji) == 1:
        if total_mashaer + new_pax != total_arrival:
            raise HTTPException(
                status_code=400,
                detail="Mashaer pax must be equal arrival pax",
            )


async def validate_between_cities_pax(
        db: AsyncSession,
        agency_name: str,
        new_pax: int,
):
    arrival_hajji = await route_request_repository.find_hajji_by_route_type(
        db=db,
        route_type="ARRIVAL",
        agency_name=agency_name,
    )

    total_arrival = sum(a.number_of_pax for a in arrival_hajji)

    if new_pax < total_arrival:
        raise HTTPException(
            status_code=400,
            detail="Between Cities pax must exceed arrival pax",
        )


async def create_route_request(db: AsyncSession, request: RouteRequestBaseSchema, agency_name: str):
    try:
        if request.total_price <= 0 or request.number_of_pax <= 0:
            raise HTTPException(status_code=400, detail="Invalid request")

        request_dict = request.model_dump(exclude_none=True)
        route_request = await route_request_repository.find_route_by_route_mapping_id(db=db,
                                                                                      route_mapping_id=request.route_mapping_id,
                                                                                      agency_name=agency_name)

        request_dict['status'] = "SEND_TO_LEAD"
        request_dict['agency_name'] = agency_name
        request_dict['created_by'] = agency_name
        request_dict['updated_by'] = agency_name

        if len(route_request) == 1:
            if route_request[0].number_of_pax != request_dict['number_of_pax']:
                raise HTTPException(status_code=400, detail="Up and Down number of pax not same")

        if request.route_type == 'MASHAER':
            await validate_mashaer_pax(db=db, agency_name=agency_name, new_pax=request.number_of_pax)

        elif request.route_type in {"BETWEEN_CITIES_UP", "BETWEEN_CITIES_DOWN"}:
            await validate_between_cities_pax(
                db=db,
                agency_name=agency_name,
                new_pax=request.number_of_pax,
            )

        agency = await admin_repository.get_agency_by_agency_name(db=db, agency_name=agency_name)
        if agency.sar < request.total_price:
            raise HTTPException(status_code=400, detail="You have not enough money in SAR")

        new_sar = agency.sar - request.total_price

        sar_update_dict = {
            'sar': new_sar,
            'agency_name': agency_name,
        }

        result = await route_request_repository.create_route_request(db=db, request_dict=request_dict,
                                                                     sar_update_dict=sar_update_dict)
        return RouteRequestResponseSchema.model_validate(result)

    except Exception as e:
        raise e


async def get_route_wise_hajji_count(db: AsyncSession, agency_name: str):
    try:
        result = await route_request_repository.get_route_wise_hajji_count(db=db, agency_name=agency_name)
        return result
    except Exception as e:
        raise e


async def get_route_requests(db:AsyncSession, agency_name:str):
    try:
        child_agencies = await admin_service.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))

        result = await route_request_repository.get_route_requests(db=db, agency_names=child_agencies)
        route_requests = [
            RouteRequestResponseSchema.model_validate(item)
            for item in result
        ]

        return RouteRequestListResponseSchema(
            route_requests=route_requests
        )
    except Exception as e:
        raise e


async def get_route_request_by_id(db:AsyncSession, request_id:int, agency_name:str):
    try:
        request = await route_request_repository.get_route_request_by_id(db=db, request_id=request_id)
        if not request:
            raise HTTPException(status_code=400, detail="Route Request not found")

        child_agencies = await admin_service.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))

        if agency_name not in child_agencies:
            raise HTTPException(status_code=400, detail="Agency name mismatches")

        return RouteRequestResponseSchema.model_validate(request)
    except Exception as e:
        raise e


async def update_route_request(db:AsyncSession, request:RouteRequestUpdateSchema, agency_name:str):
    try:
        response = await route_request_repository.get_route_request_by_id(db=db, request_id=request.id)
        if not response:
            raise HTTPException(status_code=400, detail="Route Request not found")

        child_agencies = await admin_service.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))

        if agency_name not in child_agencies:
            raise HTTPException(status_code=400, detail="Agency name mismatches")

        sar_update_dict = {}
        if request.total_price and response.total_price != request.total_price:
            agency = await admin_repository.get_agency_by_agency_name(db=db, agency_name=agency_name)

            new_sar = agency.sar + response.total_price - request.total_price
            sar_update_dict = {
                'sar': new_sar,
                'agency_name': agency_name,
            }

        request_dict = request.model_dump(exclude_none=True)
        request_dict['updated_by'] = agency_name
        request_dict['updated_at'] = get_current_time()

        result = await route_request_repository.update_route_requests(db=db, request_dict=request_dict, sar_update_dict=sar_update_dict)
        return RouteRequestResponseSchema.model_validate(result)
    except Exception as e:
        raise e