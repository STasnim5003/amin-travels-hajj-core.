from datetime import datetime

from sqlalchemy import Column, DateTime, String, Boolean, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseMixinModel:
    created_at = Column(DateTime, server_default=text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=False)
    updated_at = Column(DateTime, server_default=text("(NOW() AT TIME ZONE 'UTC') + interval '6 hours'"), nullable=False)
    created_by = Column(String, nullable=True, default=None)
    updated_by = Column(String, nullable=True, default=None)
    is_active = Column(Boolean, server_default=text('true'), nullable=False)
