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
        requisition = await umrah_requisition_repository.get_requisition_by_id(db=db, requisition_id=request.id,
                                                                               agency_name=agency_name)
        if not requisition:
            raise HTTPException(status_code=400, detail="No Requisition Found ")

        b2b_finance_update_dict = {}
        if requisition.requisition_type == "B2B" and not requisition.is_confirmed:
            b2b_finance_update_dict = {
                "amount": requisition.total_price,
                "paid_amount": 0,
                "due": requisition.total_price,
                "office_code": requisition.amin_office_code,
                "b2b_agent_name": requisition.b2b_agent_name,
                "agency_name": agency_name,
                "updated_by": username,
                "created_by": username
            }
        request_dict = request.model_dump(exclude_none=True)
        request_dict['is_confirmed'] = True
        request_dict['updated_by'] = username
        request_dict['updated_at'] = get_current_time()

        result = await umrah_confirmation_pilgrim_repository.umrah_requisition_confirmation(db, request_dict, b2b_finance_update_dict)
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
                    number_of_traveller=row["number_of_traveller"],
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
                    discount=row['discount'],
                    b2b_partial_description=row['b2b_partial_description'],
                    b2b_partial_guests=row['b2b_partial_guests'],
                    b2b_type=row['b2b_type'],
                    b2b_agent_name = row["b2b_agent_name"]
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
                number_of_traveller=row.number_of_traveller,
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
                discount=row.discount,
                is_visa=requisition.is_visa,
                is_air_ticket=requisition.air_ticket,
                is_transport=True if len(requisition.transport) > 0 else False,
                is_ziara=requisition.ziara,
                is_guide=requisition.guide,
                is_food=requisition.food,
                is_train=requisition.train,
                is_hotel=True if requisition.hotel_info else False,
                sales_person=requisition.sales_person
            )
        else:
            makkah = extract_city_info(requisition.hotel_info, "Makkah")
            madina = extract_city_info(requisition.hotel_info, "Madina")

            return UmrahConfirmedPilgrimItemSchema(
                id=requisition.id,
                amin_office_code=requisition.amin_office_code,
                reference=requisition.reference,
                number_of_traveller=requisition.number_of_traveller,
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
                    hotel=False if makkah["hotel"] or madina["hotel"] else None,
                    visa=False if requisition.is_visa else None,
                    air_ticket=False if requisition.air_ticket else None,
                    transport=False if len(requisition.transport) > 0 else None,
                    ziara=False if requisition.ziara else None,
                    guide=False if requisition.guide else None,
                    food=False if requisition.food else None,
                    train=False if requisition.train else None,
                ),
                emergency_contract_person=[],
                total_price=requisition.total_price,
                total_payment=requisition.total_payment,
                total_due=requisition.total_due,
                discount=requisition.discount,
                is_visa=requisition.is_visa,
                is_air_ticket=requisition.air_ticket,
                is_transport=True if len(requisition.transport) > 0 else False,
                is_ziara=requisition.ziara,
                is_guide=requisition.guide,
                is_food=requisition.food,
                is_train=requisition.train,
                is_hotel=True if makkah or madina else False,
                sales_person=requisition.sales_person
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