from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import umrah_requisition_repository, umrah_vendor_billing_repository
from infrastructure.schema.umrah_vendor_billing_schema import UmrahVendorBillingCreateSchema, \
    UmrahVendorBillingResponseSchema, UmrahVendorBillingDetailsResponseSchema


async def create_umrah_vendor_billing(db: AsyncSession, request: UmrahVendorBillingCreateSchema, agency_name: str,
                                      username: str):
    try:
        requisition = await umrah_requisition_repository.get_requisition_by_office_code(db=db,
                                                                                             office_code=request.amin_office_code)

        if not requisition:
            raise HTTPException(status_code=400, detail='Requisition not found')

        request_dict = request.model_dump(exclude_none=True)
        request_dict['agency_name'] = agency_name
        request_dict['created_by'] = username
        request_dict['updated_by'] = username

        result = await umrah_vendor_billing_repository.create_umrah_vendor_billing(db=db, request_dict=request_dict)
        return UmrahVendorBillingResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def get_umrah_vendor_billing(db: AsyncSession, agency_name: str):
    try:
        rows = await umrah_vendor_billing_repository.get_umrah_vendor_billing(db=db, agency_name=agency_name)

        if not rows:
            raise HTTPException(status_code=400, detail='No Billing Found')

        result = []
        for data in rows:
            result.append(
                UmrahVendorBillingDetailsResponseSchema(
                    amin_office_code=data["amin_office_code"],
                    name=data.get("name"),
                    number_of_traveller=data.get("number_of_traveller"),

                    hotels=data.get("hotels"),
                    transports=data.get("transports"),

                    visa=data.get("visa"),
                    air_ticket=data.get("air_ticket"),
                    train=data.get("train"),
                    guide=data.get("guide"),
                    ziara=data.get("ziara"),
                    food=data.get("food"),
                    others=data.get("others"),

                    child_vendors=data.get("child_services"),
                    infant_vendors=data.get("infant_services"),

                    payments=data.get("payments"),
                )
            )
        return result
    except Exception as e:
        raise e


async def get_vendor_billing_summary(db:AsyncSession, agency_name:str, vendor_name:str):
    try:
        result = await umrah_vendor_billing_repository.get_vendor_billing_summary(db=db, agency_name=agency_name, vendor_name=vendor_name)

        return [UmrahVendorBillingResponseSchema.model_validate(r) for r in result]
    except Exception as e:
        raise e