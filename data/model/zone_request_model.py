from sqlalchemy import Column, Integer, String

from data.model.base_mixin_model import Base, BaseMixinModel


class ZoneRequestModel(Base, BaseMixinModel):
    __tablename__ = "zone_request"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    agency_name = Column(String, nullable=False)
    zone_wise_tent_in_mina = Column(String, nullable=True)
    zone_wise_pilgrims = Column(Integer, nullable=True)
    service_company_in_mina_arafat = Column(String, nullable=True)
    package_in_mina_arafat = Column(String, nullable=True)
    remarks = Column(String, nullable=True)