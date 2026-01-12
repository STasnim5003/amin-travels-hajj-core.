
from sqlalchemy import Column, String, BigInteger, Boolean, Float
from sqlalchemy.dialects.postgresql import JSONB

from data.model.base_mixin_model import Base, BaseMixinModel


class AdminModel(Base, BaseMixinModel):
    __tablename__ = 'admin'
    __table_args__ = {'schema': 'core'}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="ADMIN")
    agency_name = Column(String, nullable=False)
    license_number = Column(String, nullable=False)
    location = Column(String, nullable=True)
    mobile_no = Column(String, nullable=False)
    email = Column(String, nullable=True)
    passport_copy = Column(JSONB, nullable=True)
    logo = Column(JSONB, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    google_map_location = Column(String, nullable=True)
    saudi_representatives = Column(JSONB, nullable=True)
    lead_agency = Column(String, nullable=True)
    bdt = Column(Float, nullable=True)
    sar = Column(Float, nullable=True)
    rfq_no = Column(BigInteger, nullable=True)
