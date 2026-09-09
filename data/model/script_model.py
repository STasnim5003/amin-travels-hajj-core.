from sqlalchemy import Column, String, Integer, Float, DateTime

from data.model.base_mixin_model import Base


class AgencyHajjiCountFetchModel(Base):
    __tablename__ = "hajj_agency_vouchers"
    __table_args__ = {"schema": "core"}

    hl = Column(String, primary_key=True)
    agency = Column(String, nullable=True)
    preregistered_pilgrim = Column(Integer, nullable=True)
    registered_pilgrim = Column(Integer, nullable=True)
    voucher_from_details = Column(Integer, nullable=True)
    need_to_pay_voucher = Column(Integer, nullable=True)
    percentage_registered = Column(Float, nullable=True)
    total_pilgrims = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=True)
