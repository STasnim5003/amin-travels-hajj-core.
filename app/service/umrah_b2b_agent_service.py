from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.core.utils.get_current_time import get_current_time
from data.repository import umrah_b2b_agent_repository
from infrastructure.schema.umrah_b2b_agent_schema import UmrahB2BAgentCreate, UmrahB2BAgentResponse, \
    UmrahB2BAgentListResponse, UmrahB2BAgentUpdate


async def create_umrah_b2b_agent(db:AsyncSession, request:UmrahB2BAgentCreate, agency_name:str, username:str):
    try:
        umrah_b2b_agent = await umrah_b2b_agent_repository.get_umrah_b2b_agent_by_name(db=db, b2b_agent_name = request.name, agency_name=agency_name)

        if umrah_b2b_agent:
            raise HTTPException(status_code=400, detail='Umrah B2B Agent Name already exists')

        request_dict = request.model_dump(exclude_none=True)
        request_dict['agency_name'] = agency_name
        request_dict['created_by'] = username
        request_dict['updated_by'] = username

        result = await umrah_b2b_agent_repository.create_umrah_b2b_agent(db=db, request_dict=request_dict)
        return UmrahB2BAgentResponse.model_validate(result)
    except Exception as e:
        raise e

async def get_umrah_b2b_agents(db:AsyncSession, agency_name: str):
    try:
        umrah_b2b_agents = await umrah_b2b_agent_repository.get_umrah_b2b_agents(db=db, agency_name=agency_name)

        b2b_agent_list = []
        for umrah_b2b_agent in umrah_b2b_agents:
            b2b_agent_list.append(UmrahB2BAgentResponse.model_validate(umrah_b2b_agent))

        return UmrahB2BAgentListResponse(
            b2b_agent_list=b2b_agent_list
        )
    except Exception as e:
        raise e

async def get_umrah_b2b_agent_by_id(db:AsyncSession, agency_name:str, agent_id:int):
    try:
        result = await umrah_b2b_agent_repository.get_umrah_b2b_agent_by_id(db=db, agent_id=agent_id)
        if not result:
            raise HTTPException(status_code=400, detail='Agent not found')

        if result.agency_name != agency_name:
            raise HTTPException(status_code=400, detail='Agency Name does not match')

        return UmrahB2BAgentResponse.model_validate(result)
    except Exception as e:
        raise e


async def update_b2b_agent(db:AsyncSession, request:UmrahB2BAgentUpdate, agency_name:str, username:str):
    try:
        result = await umrah_b2b_agent_repository.get_umrah_b2b_agent_by_id(db=db, agent_id=request.id)
        if not result:
            raise HTTPException(status_code=400, detail='Agent not found')

        if result.agency_name != agency_name:
            raise HTTPException(status_code=400, detail='Agency Name does not match')

        request_dict = request.model_dump(exclude_none=True)
        request_dict['updated_by'] = username
        request_dict['updated_at'] = get_current_time()
        result = await umrah_b2b_agent_repository.update_umrah_b2b_agent(db=db, request_dict=request_dict)
        return UmrahB2BAgentResponse.model_validate(result)
    except Exception as e:
        raise e


async def delete_umrah_b2b_agent(db:AsyncSession, agency_name:str, agent_id:int):
    try:
        result = await umrah_b2b_agent_repository.get_umrah_b2b_agent_by_id(db=db, agent_id=agent_id)
        if not result:
            raise HTTPException(status_code=400, detail='Agent not found')

        if result.agency_name != agency_name:
            raise HTTPException(status_code=400, detail='Agency Name does not match')

        return await umrah_b2b_agent_repository.delete_umrah_b2b_agent(db=db, agent_id=agent_id)
    except Exception as e:
        raise e