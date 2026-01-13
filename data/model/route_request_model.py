from sqlalchemy import Column, Integer, String, Float

from data.model.base_mixin_model import Base, BaseMixinModel


class RouteRequestModel(Base, BaseMixinModel):
    __tablename__ = "route_request"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    route_type = Column(String, nullable=False)
    route_name = Column(String, nullable=False)
    route_price = Column(Float, nullable=False)
    number_of_pax = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    agency_name = Column(String, nullable=False)
    status = Column(String, nullable=True)
    cancellation_status = Column(String, nullable=True)
