from sqlalchemy import Column, Integer, String, DateTime

from data.model.base_mixin_model import Base, BaseMixinModel


class AgencyProfileModel(Base, BaseMixinModel):
    __tablename__ = "agency_profile"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    sl_no = Column(Integer, nullable=True)
    hl = Column(String, nullable=False, unique=True, index=True)
    agency_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    pre_reg = Column(Integer, nullable=True)
    reg = Column(Integer, nullable=True)
    total = Column(Integer, nullable=True)
    source_updated_at = Column(DateTime(timezone=True), nullable=True)
