from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, Literal
from datetime import date
from pydantic import BaseModel
from ...utils.auth import verify_token
from ...database.db import get_db
from ...models.transaction import Transaction
from ...models.account import Account

router = APIRouter(prefix="/assets", dependencies=[Depends(verify_token)])

class BalanceHistoryItem(BaseModel):
    period: str
    period_start: str
    period_end: str
    balance: float
    change: float
    change_pct: float

class AssetHistoryResponse(BaseModel):
    current_balance: float
    balance_history: list[BalanceHistoryItem]

@router.get("/history", response_model=AssetHistoryResponse)
async def get_asset_history(
    account_id: str = Query(..., description="Target account ID"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    granularity: Literal["day", "week", "month"] = Query("month", description="Time granularity"),
    db: Session = Depends(get_db)
):
    # Verify account exists
    account = db.query(Account).filter(Account.account_id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Set default date range if not provided
    if not end_date:
        end_date = date.today()
    if not start_date:
        # Default to 12 months ago
        if granularity == "month":
            start_date = date(end_date.year - 1, end_date.month, 1)
        elif granularity == "week":
            start_date = date(end_date.year, end_date.month - 3, end_date.day) if end_date.month > 3 else date(end_date.year - 1, end_date.month + 9, end_date.day)
        else:  # day
            start_date = date(end_date.year, end_date.month - 1, end_date.day) if end_date.month > 1 else date(end_date.year - 1, 12, end_date.day)

    # Get all transactions for the account within date range
    transactions = db.query(Transaction).filter(
        and_(
            Transaction.account_id == account_id,
            Transaction.transaction_date <= end_date,
            Transaction.is_removed == False
        )
    ).order_by(Transaction.transaction_date.asc()).all()

    # Calculate current balance (sum of all transactions up to end_date)
    # Note: Plaid uses positive for expenses, negative for income
    # So we negate the amount to get actual balance change
    current_balance = sum(-float(t.amount) for t in transactions)

    # Group transactions by period and calculate balance history
    balance_history = []

    if granularity == "month":
        balance_history = _calculate_monthly_balance(transactions, start_date, end_date)
    elif granularity == "week":
        balance_history = _calculate_weekly_balance(transactions, start_date, end_date)
    else:  # day
        balance_history = _calculate_daily_balance(transactions, start_date, end_date)

    return AssetHistoryResponse(
        current_balance=current_balance,
        balance_history=balance_history
    )

def _calculate_monthly_balance(transactions, start_date: date, end_date: date) -> list[BalanceHistoryItem]:
    """Calculate balance history grouped by month"""
    from calendar import monthrange

    history = []
    current_date = start_date.replace(day=1)

    while current_date <= end_date:
        # Period boundaries
        period_start = current_date
        last_day = monthrange(current_date.year, current_date.month)[1]
        period_end = current_date.replace(day=last_day)

        # Calculate balance at end of period
        # Negate amounts because Plaid uses positive for expenses, negative for income
        balance_at_period_end = sum(
            -float(t.amount) for t in transactions
            if t.transaction_date <= period_end
        )

        # Calculate balance at end of previous period
        prev_month = current_date.month - 1 if current_date.month > 1 else 12
        prev_year = current_date.year if current_date.month > 1 else current_date.year - 1
        prev_last_day = monthrange(prev_year, prev_month)[1]
        prev_period_end = date(prev_year, prev_month, prev_last_day)

        balance_at_prev_period_end = sum(
            -float(t.amount) for t in transactions
            if t.transaction_date <= prev_period_end
        )

        # Calculate change
        change = balance_at_period_end - balance_at_prev_period_end
        change_pct = (change / balance_at_prev_period_end * 100) if balance_at_prev_period_end != 0 else 0

        history.append(BalanceHistoryItem(
            period=current_date.strftime("%Y-%m"),
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
            balance=round(balance_at_period_end, 2),
            change=round(change, 2),
            change_pct=round(change_pct, 2)
        ))

        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)

    return history

def _calculate_weekly_balance(transactions, start_date: date, end_date: date) -> list[BalanceHistoryItem]:
    """Calculate balance history grouped by week"""
    from datetime import timedelta

    history = []
    current_date = start_date - timedelta(days=start_date.weekday())  # Start from Monday

    while current_date <= end_date:
        period_start = current_date
        period_end = current_date + timedelta(days=6)  # Sunday

        # Calculate balance at end of period
        # Negate amounts because Plaid uses positive for expenses, negative for income
        balance_at_period_end = sum(
            -float(t.amount) for t in transactions
            if t.transaction_date <= period_end
        )

        # Calculate balance at end of previous period
        prev_period_end = period_start - timedelta(days=1)
        balance_at_prev_period_end = sum(
            -float(t.amount) for t in transactions
            if t.transaction_date <= prev_period_end
        )

        # Calculate change
        change = balance_at_period_end - balance_at_prev_period_end
        change_pct = (change / balance_at_prev_period_end * 100) if balance_at_prev_period_end != 0 else 0

        history.append(BalanceHistoryItem(
            period=f"{period_start.strftime('%Y-W%W')}",
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
            balance=round(balance_at_period_end, 2),
            change=round(change, 2),
            change_pct=round(change_pct, 2)
        ))

        # Move to next week
        current_date += timedelta(days=7)

    return history

def _calculate_daily_balance(transactions, start_date: date, end_date: date) -> list[BalanceHistoryItem]:
    """Calculate balance history grouped by day"""
    from datetime import timedelta

    history = []
    current_date = start_date

    while current_date <= end_date:
        # Calculate balance at end of day
        # Negate amounts because Plaid uses positive for expenses, negative for income
        balance_at_day_end = sum(
            -float(t.amount) for t in transactions
            if t.transaction_date <= current_date
        )

        # Calculate balance at end of previous day
        prev_date = current_date - timedelta(days=1)
        balance_at_prev_day_end = sum(
            -float(t.amount) for t in transactions
            if t.transaction_date <= prev_date
        )

        # Calculate change
        change = balance_at_day_end - balance_at_prev_day_end
        change_pct = (change / balance_at_prev_day_end * 100) if balance_at_prev_day_end != 0 else 0

        history.append(BalanceHistoryItem(
            period=current_date.isoformat(),
            period_start=current_date.isoformat(),
            period_end=current_date.isoformat(),
            balance=round(balance_at_day_end, 2),
            change=round(change, 2),
            change_pct=round(change_pct, 2)
        ))

        # Move to next day
        current_date += timedelta(days=1)

    return history
