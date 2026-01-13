from data.model.base_mixin_model import BaseMixinModel, Base
from sqlalchemy import Column, Integer, String, Float

class RouteForRequisition(Base, BaseMixinModel):
    __tablename__ = "routes_for_requisition"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    route_type = Column(String, nullable=False)
    route_name = Column(String, nullable=False)
    agency_name = Column(String, nullable=False)
    route_price = Column(Float, nullable=False)