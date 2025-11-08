from sqlalchemy import Column, Integer, String

from data.model.base_mixin_model import Base, BaseMixinModel


class TransportServiceModel(Base, BaseMixinModel):
    __tablename__ = 'transport_service'
    __table_args__ = {'schema': 'core'}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    seats = Column(String, nullable=False)
    agency_name = Column(String, nullable=False)
