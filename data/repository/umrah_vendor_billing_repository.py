from sqlalchemy import insert, text
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.umrah_vendor_billing_model import UmrahVendorBillingModel


async def create_umrah_vendor_billing(db: AsyncSession, request_dict: dict):
    try:
        stmt = (
            insert(UmrahVendorBillingModel)
            .values(**request_dict)
            .returning(UmrahVendorBillingModel)
        )

        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def get_umrah_vendor_billing(db: AsyncSession, agency_name: str):
    try:
        query = text("""
                SELECT
                    ur.umrah_requisition_code,
                    ur.invoice_no,
                    ur.name,
                    ur.number_of_traveller,

                    (
                        SELECT jsonb_agg(
                            jsonb_build_object(
                                'city', h ->> 'city',
                                'check_in', h ->> 'check_in',
                                'check_out', h ->> 'check_out',
                                'room_type', h ->> 'room_type',
                                'vendor_price', h -> 'price' ->> 'vendor_price',
                                'vendor_name', h -> 'price' ->> 'vendor_name'
                            )
                        )
                        FROM jsonb_array_elements(ur.hotel_info) h
                    ) AS hotels,

                    (
                        SELECT jsonb_agg(
                            jsonb_build_object(
                                'route_id', t ->> 'route_id',
                                'transport', t ->> 'transport',
                                'route_description', t ->> 'route_description',
                                'vendor_price', t -> 'price' ->> 'vendor_price',
                                'vendor_name', t -> 'price' ->> 'vendor_name'
                            )
                        )
                        FROM jsonb_array_elements(ur.transport) t
                    ) AS transports,

                    jsonb_build_object(
                        'vendor_price', ur.visa_price ->> 'vendor_price',
                        'vendor_name', ur.visa_price ->> 'vendor_name'
                    ) AS visa,

                    jsonb_build_object(
                        'vendor_price', ur.air_ticket_price ->> 'vendor_price',
                        'vendor_name', ur.air_ticket_price ->> 'vendor_name'
                    ) AS air_ticket,

                    jsonb_build_object(
                        'vendor_price', ur.train_price ->> 'vendor_price',
                        'vendor_name', ur.train_price ->> 'vendor_name'
                    ) AS train,

                    jsonb_build_object(
                        'vendor_price', ur.guide_price ->> 'vendor_price',
                        'vendor_name', ur.guide_price ->> 'vendor_name'
                    ) AS guide,

                    jsonb_build_object(
                        'vendor_price', ur.ziara_price ->> 'vendor_price',
                        'vendor_name', ur.ziara_price ->> 'vendor_name'
                    ) AS ziara,

                    jsonb_build_object(
                        'vendor_price', ur.food_price ->> 'vendor_price',
                        'vendor_name', ur.food_price ->> 'vendor_name'
                    ) AS food,

                    jsonb_build_object(
                        'vendor_price', ur.others_price ->> 'vendor_price',
                        'vendor_name', ur.others_price ->> 'vendor_name'
                    ) AS others,

                    jsonb_build_object(
                        'visa_vendor_price', ur.child_service -> 'visa' ->> 'vendor_price',
                        'visa_vendor_name', ur.child_service -> 'visa' ->> 'vendor_name',
                        'hotel_vendor_price', ur.child_service -> 'hotelbed' ->> 'vendor_price',
                        'hotel_vendor_name', ur.child_service -> 'hotelbed' ->> 'vendor_name',
                        'air_ticket_vendor_price', ur.child_service -> 'airticket' ->> 'vendor_price',
                        'air_ticket_vendor_name', ur.child_service -> 'airticket' ->> 'vendor_name'
                    ) AS child_vendors,

                    jsonb_build_object(
                        'visa_vendor_price', ur.infant_service -> 'visa' ->> 'vendor_price',
                        'visa_vendor_name', ur.infant_service -> 'visa' ->> 'vendor_name',
                        'hotel_vendor_price', ur.infant_service -> 'hotelbed' ->> 'vendor_price',
                        'hotel_vendor_name', ur.infant_service -> 'hotelbed' ->> 'vendor_name',
                        'air_ticket_vendor_price', ur.infant_service -> 'airticket' ->> 'vendor_price',
                        'air_ticket_vendor_name', ur.infant_service -> 'airticket' ->> 'vendor_name'
                    ) AS infant_vendors,

                    (
                        SELECT jsonb_agg(
                            jsonb_build_object(
                                'vendor_name', uvb.vendor_name,
                                'description', uvb.description,
                                'bill', uvb.bill,
                                'credit', uvb.credit,
                                'remarks', uvb.remarks
                            )
                        )
                        FROM core.umrah_vendor_billing uvb
                        WHERE uvb.umrah_requisition_code = ur.umrah_requisition_code
                    ) AS payments

                FROM core.umrah_requisition ur
                WHERE ur.agency_name = :agency_name
                ORDER BY ur.umrah_requisition_code DESC
            """)

        result = await db.execute(query, {"agency_name": agency_name})
        return result.mappings().all()
    except Exception as e:
        raise e
