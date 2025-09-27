from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from ..database.db import Base
from ..config.settings import settings

class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = {"schema": settings.DATABASE_SCHEMA}

    account_id = Column(String(255), primary_key=True)
    account_name = Column(String(100))
    account_official_name = Column(String(100))
    account_type = Column(String(50))
    created_at = Column(DateTime, server_default=func.current_timestamp())
    last_synced_at = Column(DateTime)