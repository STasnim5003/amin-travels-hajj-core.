from sqlalchemy import Column, Integer, String, BigInteger

from data.model.base_mixin_model import BaseMixinModel, Base


class UmrahB2BAgentModel(Base, BaseMixinModel):
    __tablename__ = "umrah_b2b_agents"
    __table_args__ = {"schema": "core"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    details = Column(String, nullable=True)

    total_bill = Column(BigInteger, nullable=False, server_default="0")
    total_due = Column(BigInteger, nullable=False, server_default="0")
    total_credit = Column(BigInteger, nullable=False, server_default="0")

    agency_name = Column(String, nullable=True)
