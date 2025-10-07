from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List

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

class TransactionListResponse(BaseModel):
    transactions: List[Transaction]
    total: int
    limit: int
    offset: int

class PeriodSummary(BaseModel):
    period: str  # e.g., "2025-01", "2025-W01", "2025", "all"
    income: float
    expense: float
    net: float
    transaction_count: int

class CategorySummary(BaseModel):
    category: str
    amount: float
    transaction_count: int
    category_type: str  # "primary" or "detailed"

class TransactionSummaryResponse(BaseModel):
    period_summaries: List[PeriodSummary]
    category_summaries: List[CategorySummary]
    total_income: float
    total_expense: float
    net_total: float
    total_transactions: int