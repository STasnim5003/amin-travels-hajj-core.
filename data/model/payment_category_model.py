from sqlalchemy import Column, Integer, String

from data.model.base_mixin_model import Base, BaseMixinModel


class PaymentCategoryModel(Base, BaseMixinModel):
    __tablename__ = "payment_category"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    agency_name = Column(String, nullable=False)
