from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Text
from sqlalchemy.dialects.postgresql import JSONB

from data.model.base_mixin_model import Base, BaseMixinModel



class PackageModel(Base, BaseMixinModel):
    __tablename__ = 'packages'
    __table_args__ = {'schema': 'core'}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    discount = Column(String, nullable=True)
    price = Column(BigInteger,  nullable=False)
    locations = Column(JSONB, nullable=False)





