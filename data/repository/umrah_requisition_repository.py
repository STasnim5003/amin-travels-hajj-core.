from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from data.model.admin_user_model import AdminUserModel
from data.model.umrah_b2b_payment_model import UmrahB2BPayment
from data.model.umrah_requisition_model import UmrahRequisitionModel, UmrahVendorsPriceModel


async def create(db: AsyncSession, request_dict: dict, b2b_payment_dict: dict):
    try:
        stmt = (
            insert(UmrahRequisitionModel)
            .values(**request_dict)
            .returning(UmrahRequisitionModel)
        )
        result = await db.execute(stmt)

        if b2b_payment_dict:
            b2b_payment_update_stmt = (
                insert(UmrahB2BPayment)
                .values(**b2b_payment_dict)
            )
            await db.execute(b2b_payment_update_stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def get_umrah_requisitions(db, agency_name):
    try:
        stmt = (
            select(UmrahRequisitionModel, AdminUserModel.name, AdminUserModel.mobile_no)
            .outerjoin(
                AdminUserModel,
                (AdminUserModel.username == UmrahRequisitionModel.assign_to)
                & (AdminUserModel.agency_name == UmrahRequisitionModel.agency_name)
            )
            .where(UmrahRequisitionModel.agency_name == agency_name)
            .order_by(UmrahRequisitionModel.id.desc())
        )
        result = await db.execute(stmt)
        return result.all()
    except Exception as e:
        raise e


async def get_requisition_by_id(db: AsyncSession, requisition_id: int, agency_name: str):
    try:
        stmt = (
            select(UmrahRequisitionModel)
            .where(UmrahRequisitionModel.id == requisition_id, UmrahRequisitionModel.agency_name == agency_name)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except Exception as e:
        raise e


async def umrah_requisition_assign_service(db: AsyncSession, request_dict: dict):
    try:
        stmt = (update(UmrahRequisitionModel)
                .where(UmrahRequisitionModel.id == request_dict.get('id'))
                .values(**request_dict)
                .returning(UmrahRequisitionModel))
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise e


async def update_umrah_requisition(db: AsyncSession, request_dict: dict, b2b_partial_invoice_finance_update: dict):
    try:
        stmt = (
            update(UmrahRequisitionModel)
            .where(UmrahRequisitionModel.id == request_dict.get("id"))
            .values(**request_dict)
            .returning(UmrahRequisitionModel)
        )

        result = await db.execute(stmt)

        if b2b_partial_invoice_finance_update:
            stmt_b2b = (
                update(UmrahB2BPayment)
                .where(
                    UmrahB2BPayment.office_code
                    == b2b_partial_invoice_finance_update["office_code"]
                )
                .values(
                    amount=b2b_partial_invoice_finance_update["amount"],
                    due=b2b_partial_invoice_finance_update["due"],
                )
            )

            await db.execute(stmt_b2b)
        await db.commit()
        return result.scalar_one_or_none()

    except Exception as e:
        await db.rollback()
        raise e


async def create_vendors_price(db: AsyncSession, request_dict: dict):
    try:
        child_service = request_dict.pop('child_service') if request_dict.get('child_service') else None
        infant_service = request_dict.pop('infant_service') if request_dict.get('infant_service') else None
        discount = request_dict.pop('discount')

        stmt = insert(UmrahVendorsPriceModel).values(**request_dict)

        stmt = stmt.on_conflict_do_update(
            index_elements=[UmrahVendorsPriceModel.umrah_requisition_id],
            set_={key: stmt.excluded[key] for key in request_dict.keys()}
        ).returning(UmrahVendorsPriceModel)

        result = await db.execute(stmt)
        vendor_price = result.scalar_one_or_none()

        # ✅ FIX: correct WHERE condition
        stmt = (
            update(UmrahRequisitionModel)
            .values(
                child_service=child_service,
                infant_service=infant_service,
                discount=discount
            )
            .where(UmrahRequisitionModel.id == request_dict.get('umrah_requisition_id'))
        )
        await db.execute(stmt)

        await db.commit()

        if vendor_price:
            vendor_price.child_service = child_service
            vendor_price.infant_service = infant_service
            vendor_price.discount = discount

        return vendor_price

    except Exception as e:
        await db.rollback()
        raise e


async def get_requisition_with_vendor_price(db: AsyncSession, requisition_id: int):
    try:
        stmt = (
            select(UmrahRequisitionModel, UmrahVendorsPriceModel)
            .join(
                UmrahVendorsPriceModel,
                UmrahVendorsPriceModel.umrah_requisition_id == UmrahRequisitionModel.id,
                isouter=True  # LEFT JOIN (so requisition still returns if no price)
            )
            .where(UmrahRequisitionModel.id == requisition_id)
        )

        result = await db.execute(stmt)
        row = result.first()

        requisition, vendors_price = row
        return requisition, vendors_price
    except Exception as e:
        raise e


async def get_requisition_by_office_code(db: AsyncSession, office_code: str):
    try:
        stmt = (
            select(UmrahRequisitionModel.amin_office_code, UmrahRequisitionModel.total_price,
                   UmrahRequisitionModel.total_payment, UmrahRequisitionModel.discount)
            .where(UmrahRequisitionModel.amin_office_code == office_code)
        )
        result = await db.execute(stmt)
        return result.first()
    except Exception as e:
        raise e


async def check_requisition_availability(db: AsyncSession, requisition_id: int, agency_name: str):
    stmt = (
        select(UmrahRequisitionModel.id)
        .where(UmrahRequisitionModel.id == requisition_id, UmrahRequisitionModel.agency_name == agency_name)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_public_requisition(
    db: AsyncSession,
    request_dict: dict
):
    try:
        # Create requisition
        insert_stmt = (
            insert(UmrahRequisitionModel)
            .values(**request_dict)
            .returning(UmrahRequisitionModel.amin_office_code)
        )

        insert_result = await db.execute(insert_stmt)
        amin_office_code = insert_result.scalar_one()

        # Update assigned admin user
        update_stmt = (
            update(AdminUserModel)
            .values(latest_assign_time=get_current_time())
            .where(
                AdminUserModel.username == request_dict.get("assign_to")
            )
            .returning(AdminUserModel)
        )

        update_result = await db.execute(update_stmt)
        admin_user = update_result.scalar_one_or_none()

        await db.commit()

        return {
            "amin_office_code": amin_office_code,
            "admin_user": admin_user,
        }

    except Exception:
        await db.rollback()
        raise