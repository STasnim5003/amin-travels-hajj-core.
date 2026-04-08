from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from app.service.umrah_requisition_service import requisition_availability_check
from data.repository import umrah_confirmation_pilgrim_repository, umrah_requisition_repository
from infrastructure.schema.umrah_requisition_schema import UmrahRequisitionConfirmedPilgrimsInfoSchema, \
    UmrahRequisitionResponseSchema, UmrahConfirmedPilgrimItemSchema, UmrahConfirmedPilgrimsResponseSchema, \
    ConfirmedPilgrimsHotelInfo, ConfirmedPilgrimsFlightInfo, ServiceConfirmationStatus, ConfirmedPilgrimsTransportInfo, \
    ConfirmedPilgrimsKSAPartDataSubmission


async def umrah_requisition_confirmation(db: AsyncSession, request: UmrahRequisitionConfirmedPilgrimsInfoSchema,
                                         agency_name: str, username: str):
    try:
        await requisition_availability_check(db=db, requisition_id=request.id, agency_name=agency_name)

        request_dict = request.model_dump(exclude_none=True)
        request_dict['is_confirmed'] = True
        request_dict['updated_by'] = username
        request_dict['updated_at'] = get_current_time()

        result = await umrah_confirmation_pilgrim_repository.umrah_requisition_confirmation(db, request_dict)
        return UmrahRequisitionResponseSchema.model_validate(result)

    except Exception as e:
        raise e


async def get_confirmed_pilgrims(db: AsyncSession, agency_name: str):
    try:
        rows = await umrah_confirmation_pilgrim_repository.get_confirmed_pilgrims(db=db, agency_name=agency_name)
        pilgrims = []

        for row in rows:
            pilgrims.append(
                UmrahConfirmedPilgrimItemSchema(
                    id=row['id'],
                    amin_office_code=row["amin_office_code"],
                    reference=row["reference"],
                    confirmed_pilgrims_family_group=row["confirmed_pilgrims_family_group"],
                    confirmed_pilgrims_basic_info=row["confirmed_pilgrims_basic_info"],
                    confirmed_pilgrims_flight_info=row["confirmed_pilgrims_flight_info"],
                    confirmed_pilgrims_hotel_info=row["confirmed_pilgrims_hotel_info"],
                    confirmed_pilgrims_transport_info=row["confirmed_pilgrims_transport_info"],
                    confirmed_pilgrims_ksa_part_data_submission=row["confirmed_pilgrims_ksa_part_data_submission"],
                    confirmed_remarks=row["confirmed_remarks"],
                    service_confirmation_status=row["service_confirmation_status"],
                    emergency_contract_person=row["emergency_contract_person"],
                    total_price=row['total_price'],
                    total_payment=row['total_payment'],
                    total_due=row['total_due'],
                    discount=row['discount']
                )
            )

        return UmrahConfirmedPilgrimsResponseSchema(
            confirmed_pilgrims=pilgrims
        )
    except Exception as e:
        raise e


async def get_confirmed_pilgrim_by_id(db: AsyncSession, agency_name: str, umrah_requisition_id: int):
    try:
        requisition = await umrah_requisition_repository.get_requisition_by_id(db=db,
                                                                               requisition_id=umrah_requisition_id,
                                                                               agency_name=agency_name)
        if not requisition:
            raise HTTPException(status_code=400, detail="No Requisition Found ")

        if requisition.is_confirmed:
            row = await umrah_confirmation_pilgrim_repository.get_confirmed_pilgrim_by_id(db=db,
                                                                                          agency_name=agency_name,
                                                                                          umrah_requisition_id=umrah_requisition_id)
            return UmrahConfirmedPilgrimItemSchema(
                id=row.id,
                amin_office_code=row.amin_office_code,
                reference=row.reference,
                confirmed_pilgrims_family_group=row.confirmed_pilgrims_family_group,
                confirmed_pilgrims_basic_info=row.confirmed_pilgrims_basic_info,
                confirmed_pilgrims_flight_info=row.confirmed_pilgrims_flight_info,
                confirmed_pilgrims_hotel_info=row.confirmed_pilgrims_hotel_info,
                confirmed_pilgrims_transport_info=row.confirmed_pilgrims_transport_info,
                confirmed_pilgrims_ksa_part_data_submission=row.confirmed_pilgrims_ksa_part_data_submission,
                confirmed_remarks=row.confirmed_remarks,
                service_confirmation_status=row.service_confirmation_status,
                emergency_contract_person=row.emergency_contract_person,
                total_price=row.total_price,
                total_payment=row.total_payment,
                total_due=row.total_due,
                discount=row.discount
            )
        else:
            makkah = extract_city_info(requisition.hotel_info, "Makkah")
            madina = extract_city_info(requisition.hotel_info, "Madina")

            return UmrahConfirmedPilgrimItemSchema(
                id=requisition.id,
                amin_office_code=requisition.amin_office_code,
                reference=requisition.reference,
                confirmed_pilgrims_family_group=requisition.confirmed_pilgrims_family_group,
                confirmed_pilgrims_basic_info=[],
                confirmed_pilgrims_flight_info=ConfirmedPilgrimsFlightInfo(
                    arrival_flight_date=requisition.flight_date_final,
                    departure_flight_date=requisition.return_date_final,
                ),
                confirmed_pilgrims_hotel_info=ConfirmedPilgrimsHotelInfo(
                    makkah_hotel=makkah.get('hotel'),
                    makkah_check_in=makkah.get('check_in'),
                    makkah_check_out=makkah.get('check_out'),
                    makkah_hotel_vendor=makkah.get('vendor'),
                    madina_hotel=madina.get('hotel'),
                    madina_check_in=madina.get('check_in'),
                    madina_check_out=madina.get('check_out'),
                    madina_hotel_vendor=madina.get('vendor')
                ),
                confirmed_pilgrims_transport_info=ConfirmedPilgrimsTransportInfo(),
                confirmed_pilgrims_ksa_part_data_submission=ConfirmedPilgrimsKSAPartDataSubmission(),
                confirmed_remarks=requisition.confirmed_remarks,
                service_confirmation_status=ServiceConfirmationStatus(
                    hotel="FALSE" if makkah["hotel"] or madina["hotel"] else "NOT_APPLICABLE",
                    visa="FALSE" if requisition.is_visa is True else "NOT_APPLICABLE",
                    air_ticket="FALSE" if requisition.air_ticket is True else "NOT_APPLICABLE",
                    transport="FALSE" if len(requisition.transport) > 0 else "NOT_APPLICABLE",
                    ziara="FALSE" if requisition.ziara is True else "NOT_APPLICABLE",
                    guide="FALSE" if requisition.guide is True else "NOT_APPLICABLE",
                    food="FALSE" if requisition.food is True else "NOT_APPLICABLE",
                    train="FALSE" if requisition.train is True else "NOT_APPLICABLE",
                ),
                emergency_contract_person=[],
                total_price=requisition.total_price,
                total_payment=requisition.total_payment,
                total_due=requisition.total_due,
                discount=requisition.discount
            )
    except Exception as e:
        raise e


def extract_city_info(hotel_info, city_name):
    for item in hotel_info or []:
        if item.get("city") == city_name:
            return {
                "hotel": item.get("hotels", [{}])[0].get("hotel_name"),
                "check_in": item.get("check_in"),
                "check_out": item.get("check_out"),
                "vendor": item.get("price", {}).get("vendor_name"),
            }
    return {
        "hotel": None,
        "check_in": None,
        "check_out": None,
        "vendor": None,
    }