from sqlalchemy import Column, DateTime, Integer, String, text

from data.model.base_mixin_model import Base


class AgencyProfileModel(Base):
    __tablename__ = 'hajj_agency_profile'
    __table_args__ = {'schema': 'core'}

    hl = Column(String(10), primary_key=True)
    sl_no = Column(Integer, nullable=True)
    agency_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    pre_reg = Column(Integer, nullable=True)
    reg = Column(Integer, nullable=True)
    total = Column(Integer, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=text("(NOW() AT TIME ZONE 'Asia/Dhaka')"))
