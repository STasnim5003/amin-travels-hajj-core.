from sqlalchemy import Column, Integer, String, Boolean

from data.model.base_mixin_model import Base, BaseMixinModel


class RouteModel(Base, BaseMixinModel):
    __tablename__ = "route"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    description = Column(String, nullable=False)
    is_publish = Column(Boolean, nullable=False, server_default="false")
    agency_name = Column(String, nullable=True)