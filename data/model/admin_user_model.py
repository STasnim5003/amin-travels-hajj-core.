from sqlalchemy import Column, Integer, String

from data.model.base_mixin_model import BaseMixinModel, Base


class AdminUserModel(Base, BaseMixinModel):
    __tablename__ = "admin_user"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    mobile_no = Column(String, nullable=False)
    role = Column(String, nullable=False)
    agency_name = Column(String, nullable=False)
    passport_no = Column(String, nullable=True)
    passport_expiry_date = Column(String, nullable=True)
    passport_address = Column(String, nullable=True)
    passport_dob = Column(String, nullable=True)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    code = Column(String, nullable=True)
    total_payable = Column(Integer, nullable=True)
    total_due = Column(Integer, nullable=True)
    total_payment = Column(Integer, nullable=True)