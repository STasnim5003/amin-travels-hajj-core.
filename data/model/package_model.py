from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Text
from data.model.base_mixin_model import Base, BaseMixinModel



class PackageModel(Base, BaseMixinModel):
    __tablename__ = 'packages'
    __table_args__ = {'schema': 'core'}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, index=True,  nullable=False)
    price = Column(BigInteger,  nullable=False)





