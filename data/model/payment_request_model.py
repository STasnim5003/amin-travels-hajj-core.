from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.dialects.postgresql import JSONB

from data.model.base_mixin_model import Base, BaseMixinModel


class PaymentRequestModel(Base, BaseMixinModel):
    __tablename__ = "payment_request_b2b"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    payment_way = Column(String, nullable=False)
    money_receipt_payment_slip_file = Column(JSONB, nullable=True)
    reference_number = Column(String, nullable=True)
    transaction_id = Column(String, nullable=True)
    money_receipt_number = Column(String, nullable=True)
    status = Column(String, nullable=True)
    agency_name = Column(String, nullable=True)
    purpose = Column(String, nullable=True)
    details = Column(String, nullable=True)
    payment_date = Column(String, nullable=True)
    amount = Column(Float, nullable=True)
    exchange_rate = Column(Float, nullable=True)
    sector = Column(String, nullable=True)
    remarks = Column(String, nullable=True)
    nusuk_request_id = Column(String, nullable=True)
    exchanged_amount = Column(Float, nullable=True)
