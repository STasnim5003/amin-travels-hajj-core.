from sqlalchemy import update, text
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.umrah_requisition_model import UmrahRequisitionModel


async def umrah_requisition_confirmation(db: AsyncSession, request_dict: dict):
    try:
        stmt = (
            update(UmrahRequisitionModel)
            .where(UmrahRequisitionModel.id == request_dict.get('id'))
            .values(**request_dict)
            .returning(UmrahRequisitionModel)
        )

        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def get_confirmed_pilgrims(db: AsyncSession, agency_name: str):
    try:
        query = text("""
                SELECT 
                    ur.id,
                    ur.amin_office_code,
                    ur.reference,
                    ur.service_confirmation_status,
                    ur.number_of_traveller,
                    ur.confirmed_pilgrims_family_group,
                    ur.confirmed_pilgrims_basic_info,
                    ur.confirmed_pilgrims_flight_info,
                    ur.confirmed_pilgrims_hotel_info,
                    ur.confirmed_pilgrims_transport_info,
                    ur.confirmed_pilgrims_ksa_part_data_submission,
                    ur.emergency_contract_person,
                    ur.confirmed_remarks,
                    ur.total_price, 
                    ur.total_payment, 
                    ur.total_due, 
                    ur.discount
                FROM core.umrah_requisition ur
                WHERE ur.agency_name = :agency_name 
                  AND ur.is_confirmed = TRUE
                ORDER BY ur.id DESC
            """)

        result = await db.execute(query, {"agency_name": agency_name})
        return result.mappings().all()
    except Exception as e:
        raise e


async def is_pilgrim_confirmed(db: AsyncSession, agency_name: str, umrah_requisition_id: int):
    try:
        query = text("""
            SELECT id, is_confirmed
            FROM core.umrah_requisition
            WHERE agency_name = :agency_name
                AND id = :umrah_requisition_id
        """)

        result = await db.execute(query, {"agency_name": agency_name, "umrah_requisition_id": umrah_requisition_id})
        return result.scalars().all()
    except Exception as e:
        raise e


async def get_confirmed_pilgrim_by_id(db: AsyncSession, agency_name: str, umrah_requisition_id: int):
    try:
        query = text("""
                SELECT 
                    ur.id,
                    ur.amin_office_code,
                    ur.reference,
                    ur.number_of_traveller,
                    ur.service_confirmation_status,
                    ur.confirmed_pilgrims_family_group,
                    ur.confirmed_pilgrims_basic_info,
                    ur.confirmed_pilgrims_flight_info,
                    ur.confirmed_pilgrims_hotel_info,
                    ur.confirmed_pilgrims_transport_info,
                    ur.confirmed_pilgrims_ksa_part_data_submission,
                    ur.emergency_contract_person,
                    ur.confirmed_remarks,
                    ur.total_price, 
                    ur.total_payment, 
                    ur.total_due, 
                    ur.discount
                FROM core.umrah_requisition ur
                WHERE ur.id = :umrah_requisition_id
                    AND ur.agency_name = :agency_name
            """)

        result = await db.execute(query, {"umrah_requisition_id": umrah_requisition_id, "agency_name": agency_name})
        return result.fetchone()
    except Exception as e:
        raise e
