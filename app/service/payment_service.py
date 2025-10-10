from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import payment_repository
from infrastructure.schema.payment_schema import PaymentSchema, PaymentResponseSchema, \
    PaginatedPaymentResponseForGroupLeader, PaginatedPaymentResponseForAgency, AgencyPaymentSchemaForGroupLeader


async def create_payable_for_group_leader(db: AsyncSession, payment_request: PaymentSchema, agency_name: str):
    try:
        return await payment_repository.create_payable_for_group_leader(db, payment_request, agency_name)
    except Exception as e:
        raise e


async def create_group_leader_payment(db: AsyncSession, request: AgencyPaymentSchemaForGroupLeader, agency_name: str):
    try:
        return await payment_repository.create_payment_for_group_leader(db, request, agency_name)
    except Exception as e:
        raise e


async def get_group_leader_payments(
        db,
        group_leader: str,
        category: str | None,
        page: int,
        size: int
):
    (
        payments,
        total,
        group_leader_total_payable,
        group_leader_total_payment,
        group_leader_total_due
    ) = await payment_repository.get_payments_by_group_leader(db, group_leader, category, page, size)

    payment_list = [PaymentResponseSchema.model_validate(p) for p in payments]

    payables = [p for p in payment_list if p.payable_id is None]
    non_payables = [p for p in payment_list if p.payable_id is not None]

    # Map non-payables to their payables
    for payable in payables:
        related_payments = [p for p in non_payables if p.payable_id == payable.id]

        payable.payments = related_payments
        payable.total_payable = payable.amount
        payable.total_paid = sum(p.amount for p in related_payments)
        payable.total_due = payable.total_payable - payable.total_paid

    return PaginatedPaymentResponseForGroupLeader(
        payments=payables,
        page=page,
        size=size,
        total=total,
        total_payable=group_leader_total_payable,
        total_payment=group_leader_total_payment,
        total_due=group_leader_total_due
    )


async def get_agency_payments(
        db,
        agency_name: str,
        group_leader: str | None,
        category: str | None,
        page: int,
        size: int
):
    (
        payments,
        total
    ) = await payment_repository.get_payments_by_agency(db, agency_name, group_leader, category, page, size)

    payment_list = [PaymentResponseSchema.model_validate(p) for p in payments]

    payables = [p for p in payment_list if p.payable_id is None]
    non_payables = [p for p in payment_list if p.payable_id is not None]

    # Map non-payables to their payables
    for payable in payables:
        related_payments = [p for p in non_payables if p.payable_id == payable.id]

        payable.payments = related_payments
        payable.total_payable = payable.amount
        payable.total_paid = sum(p.amount for p in related_payments)
        payable.total_due = payable.total_payable - payable.total_paid

    return PaginatedPaymentResponseForAgency(
        payments=payables,
        page=page,
        size=size,
        total=total
    )
