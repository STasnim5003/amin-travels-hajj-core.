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
    pilgrims_tracking_id = Column(JSON, nullable=True)
    group_leader = Column(String, nullable=True)
    category = Column(String, nullable=False)
    transaction_id = Column(String, nullable=True)
    no_of_hajji = Column(Integer, nullable=True)
    payable_id = Column(Integer, nullable=True)
    receipt = Column(JSON, nullable=True)
    tracking_id = Column(String, nullable=True)
    payment_category = Column(String, nullable=True)
    way_of_payment = Column(String, nullable=True)
    bank_info_id = Column(Integer, nullable=True)
    transfer_no = Column(String, nullable=True)
    cheque_no = Column(String, nullable=True)
    cheque_bank = Column(String, nullable=True)
    voucher_no = Column(String, nullable=True)