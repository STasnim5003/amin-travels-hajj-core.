from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Text, JSON
from data.model.base_mixin_model import Base, BaseMixinModel
from data.model.package_model import PackageModel
from data.model.user_model import UserModel


class PaymentModel(Base, BaseMixinModel):
    __tablename__ = 'payment'
    __table_args__ = {'schema': 'core'}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    description = Column(String, nullable=True)
    date = Column(String, nullable=True)
    amount = Column(Integer, nullable=False)
    pilgrims_id = Column(JSON, nullable=True)
    group_leader = Column(String, nullable=True)
    category = Column(String, nullable=False)
    transaction_id = Column(String, nullable=True)
    no_of_hajji = Column(Integer, nullable=True)