from sqlalchemy import Column, String, BigInteger, Boolean, JSON, Integer, text

from data.model.base_mixin_model import Base, BaseMixinModel


class PilgrimDataModel(Base, BaseMixinModel):
    __tablename__ = 'pilgrim_data'
    __table_args__ = {'schema': 'core'}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name_bn = Column(String, nullable=False)
    name_en = Column(String, nullable=False)
    father_name = Column(String, nullable=True)
    spouse_name = Column(String, nullable=True)
    occupation = Column(String, nullable=True)
    nid = Column(String, nullable=False)
    voucher = Column(String, nullable=True)
    type = Column(String, nullable=True)
    listed_in = Column(String, nullable=True)
    mother_name = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    management = Column(String, nullable=True)
    mobile_no = Column(String, nullable=True)
    passport_address = Column(String, nullable=True)
    present_address = Column(String, nullable=True)
    permanent_address = Column(String, nullable=True)
    tracking_id = Column(String, nullable=True)
    serial_no = Column(String, nullable=True)
    group_name = Column(String, nullable=True)
    registration_status = Column(String, nullable=True)
    password = Column(String, nullable=True)
    preliminary_password = Column(String, nullable=True)
    is_assigned = Column(Boolean)
    allocation_status = Column(String)
    package_id = Column(Integer, nullable=True)
    passport_copy = Column(JSON, nullable=True)
    vaccination_center = Column(String, nullable=True)
    comment_on_package = Column(String, nullable=True)
    reference = Column(String, nullable=True)
    group_leader = Column(String, nullable=True)
    passport_no = Column(String, nullable=True)
    total_payable = Column(Integer, nullable=True)
    total_payment = Column(Integer, nullable=True)
    package_name = Column(String, nullable=True)
    package_duration = Column(Integer, nullable=True)
    package_bed_types = Column(String, nullable=True)
    add_ons_services = Column(JSON, nullable=True)
    is_package_assigned = Column(Boolean, nullable=False, server_default=text('false'))
    total_due = Column(Integer, nullable=True)
    total_available_amount = Column(Integer, nullable=True)
    actual_payable = Column(Integer, nullable=True)
    package_price_discount = Column(Integer, nullable=True)
    lead_agency = Column(String, nullable=True)
    sub_reference = Column(String, nullable=True)
    pre_reg_voucher = Column(String, nullable=True)
    reg_voucher = Column(String, nullable=True)
    passport_dob = Column(String, nullable=True)
    passport_expiry_date = Column(String, nullable=True)
    passport_type = Column(String, nullable=True)
    second_nationality = Column(String, nullable=True)
    family_code = Column(String, nullable=True)
    sub_group = Column(String, nullable=True)
    remarks = Column(String, nullable=True)
    email = Column(String, nullable=True)
    interested_in_package = Column(String, nullable=True)
    hajj_year=Column(Integer, nullable=True)


class ReplacedPilgrimModel(Base, BaseMixinModel):
    __tablename__ = 'replaced_pilgrim'
    __table_args__ = {'schema': 'core'}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    tracking_id = Column(String, nullable=False)
    name_en = Column(String, nullable=False)
    replaced_tracking_id = Column(String, nullable=False)
    replaced_name_en = Column(String, nullable=False)
    agency_name = Column(String, nullable=False)


class TrainingSessionAndPreRegisterEnquiryPilgrim(Base, BaseMixinModel):
    __tablename__ = 'book_training_session_and_pre_register_customer'
    __table_args__ = {'schema': 'core'}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name_en = Column(String, nullable=False)
    father_name = Column(String, nullable=True)
    mobile_no = Column(String, nullable=False)
    email = Column(String, nullable=True)
    interested_in_package = Column(String, nullable=True)
    remarks = Column(String, nullable=True)
    number_of_people = Column(Integer, nullable=True)
    media = Column(String, nullable=True)
    purpose = Column(String, nullable=True)
    agency_name = Column(String, nullable=True)
