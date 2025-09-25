from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from ..database.db import Base

class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = {"schema": "cibc_budget_tracker_sandbox"}

    account_id = Column(String(255), primary_key=True)
    institution_name = Column(String(100), nullable=False)
    account_name = Column(String(100))
    account_type = Column(String(50))
    created_at = Column(DateTime, server_default=func.current_timestamp())
    last_synced_at = Column(DateTime)