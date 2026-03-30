import fastapi
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.core.utils.authorize_api import check_agency_or_staff_user
from app.service import umrah_b2b_agent_service
from data.db.db_config import get_async_db
from infrastructure.schema.umrah_b2b_agent_schema import UmrahB2BAgentCreate, UmrahB2BAgentResponse, \
    UmrahB2BAgentListResponse, UmrahB2BAgentUpdate

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private", tags=["Umrah B2B Agent"])


@private_router.post("/umrah/b2b-agent", response_model=UmrahB2BAgentResponse)
async def create_umrah_b2b_agent(
        request: UmrahB2BAgentCreate,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user),
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    username = current_user["username"]
    return await umrah_b2b_agent_service.create_umrah_b2b_agent(db=db, request=request, agency_name=agency_name,
                                                                username=username)


@private_router.get("/umrah/b2b-agent", response_model=UmrahB2BAgentListResponse)
async def get_umrah_b2b_agent(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user),
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await umrah_b2b_agent_service.get_umrah_b2b_agents(db=db, agency_name=agency_name)

@private_router.put("/umrah/b2b-agent", response_model=UmrahB2BAgentResponse)
async def update_b2b_agent(
        request: UmrahB2BAgentUpdate,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user),
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    username = current_user["username"]
    return await umrah_b2b_agent_service.update_b2b_agent(db=db, request=request, agency_name=agency_name,
                                                          username=username)

@private_router.get("/umrah/b2b-agent/{agent_id}", response_model=UmrahB2BAgentResponse)
async def get_umrah_b2b_agent_by_id(
        agent_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user),
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await umrah_b2b_agent_service.get_umrah_b2b_agent_by_id(db=db, agency_name=agency_name, agent_id=agent_id)

@private_router.delete("/umrah/b2b-agent/{agent_id}")
async def delete_umrah_b2b_agent(
        agent_id:int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user),
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await umrah_b2b_agent_service.delete_umrah_b2b_agent(db=db, agency_name=agency_name, agent_id=agent_id)