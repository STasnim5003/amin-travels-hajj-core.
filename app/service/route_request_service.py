from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from app.service import admin_service
from data.repository import route_request_repository, admin_repository
from infrastructure.schema.route_request_schema import RouteRequestBaseSchema, RouteRequestResponseSchema, \
    RouteRequestListResponseSchema, RouteRequestUpdateSchema, RouteRequestCreateSchema



async def create_route_request(db: AsyncSession, request: RouteRequestCreateSchema, agency_name: str):
    try:
        route_requests = request.route_requests
        request_dict_list = []
        total_price = request.total_price

        for r in route_requests:
            request_dict = r.model_dump(exclude_none=True)
            request_dict['status'] = "SEND_TO_LEAD"
            request_dict['agency_name'] = agency_name
            request_dict['created_by'] = agency_name
            request_dict['updated_by'] = agency_name

            request_dict_list.append(request_dict)



        agency = await admin_repository.get_agency_by_agency_name(db=db, agency_name=agency_name)
        if agency.sar < total_price:
            raise HTTPException(status_code=400, detail="You have not enough money in SAR")

        new_sar = agency.sar - total_price

        sar_update_dict = {
            'sar': new_sar,
            'agency_name': agency_name,
        }

        result = await route_request_repository.create_route_request(db=db, request_dict=request_dict_list,
                                                                     sar_update_dict=sar_update_dict)
        responses = [
            RouteRequestResponseSchema.model_validate(item)
            for item in result
        ]

        return RouteRequestListResponseSchema(
            route_requests=responses
        )
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


async def delete_route_request(db:AsyncSession, requisition_id:int, agency_name:str):
    try:
        response = await route_request_repository.get_route_request_by_id(db=db, request_id=requisition_id)
        if not response:
            raise HTTPException(status_code=400, detail="Route Request not found")

        child_agencies = await admin_service.get_child_agencies(db=db, lead_agency_name=agency_name)
        child_agencies.append(agency_name)
        child_agencies = list(set(child_agencies))

        if agency_name not in child_agencies:
            raise HTTPException(status_code=400, detail="Agency name mismatches")

        agency = await admin_repository.get_agency_by_agency_name(db=db, agency_name=agency_name)

        new_sar = agency.sar + response.total_price
        sar_update_dict = {
            'sar': new_sar,
            'agency_name': agency_name,
        }
        return await route_request_repository.delete_route_request(db=db, request_id=requisition_id, sar_update_dict=sar_update_dict)
    except Exception as e:
        raise e


async def cancel_request(db, request_id, agency_name):
    try:
        result = await route_request_repository.get_route_request_by_id(db=db, request_id=request_id)
        if not result:
            raise HTTPException(status_code=400, detail="Route Request not found")
        if result.status == 'SEND_TO_LEAD':
            raise HTTPException(status_code=400, detail="Can't Cancel Request. Edit/Delete it")
        if result.agency_name != agency_name:
            raise HTTPException(status_code=400, detail="Agency name does not match")

        request_dict = {
            'cancellation_status': "REQUEST_FOR_CANCELLATION",
            'id': request_id,
            'updated_by': agency_name,
            'updated_at': get_current_time()
        }

        result = await route_request_repository.cancel_route_request(db=db, request_dict=request_dict)
        if not result:
            raise HTTPException(status_code=400, detail="Update Route Request failed")
        return result
    except Exception as e:
        raise e


async def cancel_request_lead_agency_action(db:AsyncSession, request_id:int, agency_name:str, status:str):
    try:
        result = await route_request_repository.get_route_request_by_id(db=db, request_id=request_id)
        if not result:
            raise HTTPException(status_code=400, detail="Route Request not found")
        if result.cancellation_status != 'REQUEST_FOR_CANCELLATION':
            raise HTTPException(status_code=400, detail="Can't Approved or Rejected")

        is_lead_agency = await admin_repository.check_lead_agency_for_specific_sub_agency(db=db,
                                                                                          sub_agency=result.agency_name,
                                                                                          lead_agency=agency_name)
        if not is_lead_agency:
            raise HTTPException(status_code=400, detail="This is not your sub agency")

        request_dict = {
            'id': request_id,
            'updated_by': agency_name,
            'updated_at': get_current_time(),
            'cancellation_status': status if status == "REJECTED" else None,
        }

        result = await route_request_repository.cancel_request_lead_agency_action(db=db, request_dict=request_dict)
        if not result:
            raise HTTPException(status_code=400, detail="Update Route Request failed")
        return result
    except Exception as e:
        raise e