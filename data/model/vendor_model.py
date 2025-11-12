from sqlalchemy import Column, Integer, String

from data.model.base_mixin_model import Base, BaseMixinModel


class VendorModel(Base, BaseMixinModel):
    __tablename__ = "vendor"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    area = Column(String, nullable=True)
    agency_name = Column(String, nullable=True)
