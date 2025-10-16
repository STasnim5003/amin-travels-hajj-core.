from sqlalchemy import Column, BigInteger, String

from data.model.base_mixin_model import BaseMixinModel, Base


class BankInfoModel(Base, BaseMixinModel):
    __tablename__ = 'bank_info'
    __table_args__ = {'schema': 'core'}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    account_no = Column(String, nullable=True)
    branch = Column(String, nullable=True)
    agency_name = Column(String, nullable=False)