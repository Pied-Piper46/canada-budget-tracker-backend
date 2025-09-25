from sqlalchemy import Column, String, Numeric, Date, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from ..database.db import Base

class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {"schema": "cibc_budget_tracker_sandbox"}

    transaction_id = Column(String(255), primary_key=True)
    account_id = Column(String(255), ForeignKey("cibc_budget_tracker_sandbox.accounts.account_id", ondelete="CASCADE"))
    amount = Column(Numeric(15, 2), nullable=False)
    transaction_date = Column(Date, nullable=False)
    merchant_name = Column(String(255))
    name = Column(String(255))
    pending = Column(Boolean, default=False)
    pending_transaction_id = Column(String(255))
    personal_finance_category_primary = Column(String(100))
    personal_finance_category_detailed = Column(String(100))
    custom_category_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp())
    is_removed = Column(Boolean, default=False)