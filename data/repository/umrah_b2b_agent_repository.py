from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete
from data.model.umrah_b2b_agent_model import UmrahB2BAgentModel


async def get_umrah_b2b_agent_by_name(db:AsyncSession, b2b_agent_name:str, agency_name:str):
    try:
        stmt = (
            select(UmrahB2BAgentModel)
            .where(UmrahB2BAgentModel.name == b2b_agent_name, UmrahB2BAgentModel.agency_name == agency_name)
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except Exception as e:
        raise e


async def create_umrah_b2b_agent(db:AsyncSession, request_dict:dict):
    try:
        stmt = (
            insert(UmrahB2BAgentModel)
            .values(**request_dict)
            .returning(UmrahB2BAgentModel)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e

async def get_umrah_b2b_agents(db:AsyncSession, agency_name:str):
    try:
        stmt = (
            select(UmrahB2BAgentModel)
            .where(UmrahB2BAgentModel.agency_name == agency_name)
        )

        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        raise e

async def get_umrah_b2b_agent_by_id(db:AsyncSession, agent_id:int):
    try:
        stmt = (
            select(UmrahB2BAgentModel)
            .where(UmrahB2BAgentModel.id == agent_id)
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except Exception as e:
        raise e

async def update_umrah_b2b_agent(db:AsyncSession, request_dict:dict):
    try:
        stmt = (
            update(UmrahB2BAgentModel)
            .values(**request_dict)
            .where(UmrahB2BAgentModel.id == request_dict['id'])
            .returning(UmrahB2BAgentModel)
        )

        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e

async def delete_umrah_b2b_agent(db:AsyncSession, agent_id:int):
    try:
        stmt = (
            delete(UmrahB2BAgentModel)
            .where(UmrahB2BAgentModel.id == agent_id)
        )
        await db.execute(stmt)
        await db.commit()
        return True
    except Exception as e:
        raise e