from typing import Optional

from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from data.repository import route_for_requisition_repository, admin_repository
from infrastructure.schema.route_for_requistion_schema import RouteForRequisitionBaseSchema, \
    RouteForRequisitionListResponseSchema, RouteForRequisitionResponseSchema, RouteForRequisitionUpdateSchema


async def create_route(db:AsyncSession, route:RouteForRequisitionBaseSchema, agency_name:str):
    try:
        existing_route = await route_for_requisition_repository.get_route_by_type_and_name(db=db, route_type=route.route_type, route_name=route.route_name,agency_name=agency_name)
        if existing_route:
            raise HTTPException(status_code=400, detail='Route with this name and type already exists')

        route_request = route.model_dump(exclude_none=True)
        route_request['agency_name'] = agency_name
        route_request['created_by'] = agency_name
        route_request['updated_by'] = agency_name

        return await route_for_requisition_repository.create_route_for_requisition(db=db, route_request=route_request)
    except Exception as e:
        raise e


async def get_routes(db:AsyncSession, route_type:Optional[str], agency_name:str):
    try:
        child_agencies = await admin_repository.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))
        result = await route_for_requisition_repository.get_routes(db=db, route_type=route_type, agency_names=child_agencies)
        return RouteForRequisitionListResponseSchema.model_validate(
            {"routes": result},
            from_attributes=True
        )
    except Exception as e:
        raise e


async def get_routes_by_id(db:AsyncSession, requisition_id:int, agency_name:str):
    try:
        child_agencies = await admin_repository.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))

        result = await route_for_requisition_repository.get_routes_by_id(db=db, requisition_id=requisition_id, agency_names=child_agencies)
        return RouteForRequisitionResponseSchema.model_validate(result)

    except Exception as e:
        raise e


async def update_route(db:AsyncSession, request:RouteForRequisitionUpdateSchema, agency_name:str):
    try:
        child_agencies = await admin_repository.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))
        route = await route_for_requisition_repository.get_routes_by_id(db=db, requisition_id=request.id, agency_names=child_agencies)

        if not route:
            raise HTTPException(status_code=400, detail='Route with this name and type does not exist')

        request_dict = request.model_dump(exclude_none=True)
        request_dict['updated_by'] = agency_name
        request_dict['updated_at'] = get_current_time()

        result = await route_for_requisition_repository.update_route(db=db, route_request=request_dict)
        return RouteForRequisitionResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def delete_routes(db:AsyncSession, requisition_id:int, agency_name:str):
    try:
        child_agencies = await admin_repository.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))
        route = await route_for_requisition_repository.get_routes_by_id(db=db, requisition_id=requisition_id,
                                                                        agency_names=child_agencies)

        if not route:
            raise HTTPException(status_code=400, detail='Route with this name and type does not exist')

        return await route_for_requisition_repository.delete_route(db=db, requisition_id=requisition_id)
    except Exception as e:
        raise e