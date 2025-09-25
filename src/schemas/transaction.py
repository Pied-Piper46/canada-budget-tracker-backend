from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class TransactionBase(BaseModel):
    transaction_id: str
    account_id: str
    amount: float
    transaction_date: date
    merchant_name: Optional[str] = None
    name: Optional[str] = None
    pending: bool = False
    pending_transaction_id: Optional[str] = None
    personal_finance_category_primary: Optional[str] = None
    personal_finance_category_detailed: Optional[str] = None
    custom_category_id: Optional[int] = None

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    created_at: datetime
    updated_at: datetime
    is_removed: bool = False

    class Config:
        from_attributes = True