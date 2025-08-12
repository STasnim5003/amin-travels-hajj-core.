from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Text
from data.model.base_mixin_model import Base, BaseMixinModel
from data.model.package_model import PackageModel
from data.model.user_model import UserModel


class PaymentInfoModel(Base, BaseMixinModel):
    __tablename__ = 'payment_info'
    __table_args__ = {'schema': 'core'}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    payee = Column(BigInteger, ForeignKey(UserModel.id), index=True, nullable=False)
    package_id = Column(BigInteger, ForeignKey(PackageModel.id),  nullable=False)
    total_amount = Column(BigInteger, nullable=False, default=0)
    discount_amount = Column(BigInteger, nullable=False, default=0)
    amount_to_pay = Column(BigInteger, nullable=False, default=0)
    paid_amount = Column(BigInteger, nullable=False, default=0)
    # payment_status = Column(Integer, nullable=False)