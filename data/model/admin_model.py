
from sqlalchemy import Column, String, BigInteger, Boolean, Float, Integer, Text
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
    flight_requested = Column(Integer, nullable=True)
    route_requested = Column(Integer, nullable=True)
    hotel_requested = Column(Integer, nullable=True)
    # letterhead / signing details printed on receipts, invoices and umrah requests
    agency_name_bn = Column(Text, nullable=True)
    umrah_license_number = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    office_phone = Column(Text, nullable=True)
    office_email = Column(Text, nullable=True)
    website = Column(Text, nullable=True)
    billing_contact = Column(JSONB, nullable=True)
    bank_accounts = Column(JSONB, nullable=True)
    signature = Column(JSONB, nullable=True)
    seal = Column(JSONB, nullable=True)
    signatory_name = Column(Text, nullable=True)
    signatory_designation = Column(Text, nullable=True)
