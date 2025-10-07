from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from pydantic import BaseModel
from typing import List
from ...database.db import get_db
from ...models.account import Account
from ...models.transaction import Transaction
from ...schemas.transaction import Transaction as TransactionSchema
from ...models.sync_cursor import SyncCursor
from ...api.plaid.client import get_plaid_client
from ...utils.auth import verify_session_token
from ...config.settings import settings
from ...services.plaid import check_item_status
import time
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transactions")
security = HTTPBearer()

class SyncResponse(BaseModel):
    transactions: List[TransactionSchema]
    cursor: str

def handle_sync_error(e, access_token: str):
    if hasattr(e, 'error_code'):
        if e.error_code == 'TRANSACTIONS_SYNC_LIMIT':
            logger.warning(f"Rate limit exceedded for /transactions/sync: {access_token[:10]}...")
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
        elif e.error_code == 'TRANSACTIONS_SYNC_MUTATION_DURING_PAGINATION':
            logger.warning(f"Pagination mutation during sync: Restarting loop for {access_token[:10]}...")
            raise HTTPException(status_code=500, detail="Sync interrupted. Restarting update.")
    raise HTTPException(status_code=500, detail=str(e))

@router.get("/sync", response_model=SyncResponse)
async def sync_transactions(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    if not verify_session_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid session token")

    client = get_plaid_client()
    access_token = settings.PLAID_ACCESS_TOKEN

    # Check item status before syncing
    check_item_status(access_token)

    cursor_record = db.query(SyncCursor).first()
    cursor = cursor_record.cursor if cursor_record else ""

    request = TransactionsSyncRequest(
        access_token=access_token,
        cursor=cursor,
        count=500 # maximum txs to get once
    )

    processed_transactions = []
    retry_count = 0
    max_retries = 3 # just in the case that too many request are called. fix whatever you want.

    try:
        while True:
            response = client.transactions_sync(request)
            for added in response["added"]:
                if not db.query(Account).filter(Account.account_id == added["account_id"]).first():
                    raise HTTPException(status_code=400, detail=f"Account {added['account_id']} not found")

                db_transaction = Transaction(
                    transaction_id=added["transaction_id"],
                    account_id=added["account_id"],
                    amount=added["amount"],
                    transaction_date=added["date"],
                    merchant_name=added.get("merchant_name"),
                    name=added.get("name"),
                    pending=added["pending"],
                    personal_finance_category_primary=added["personal_finance_category"]["primary"] if added.get("personal_finance_category") else None,
                    personal_finance_category_detailed=added["personal_finance_category"]["detailed"] if added.get("personal_finance_category") else None,
                )
                db.merge(db_transaction)
                processed_transactions.append(db_transaction)

            for modified in response["modified"]:
                db_transaction = db.query(Transaction).filter(Transaction.transaction_id == modified["transaction_id"]).first()
                if db_transaction:
                    db_transaction.account_id = modified["account_id"]
                    db_transaction.amount = modified["amount"]
                    db_transaction.pending = modified["pending"]
                    db_transaction.updated_at = func.current_timestamp()
                    db.merge(db_transaction)

            for removed in response["removed"]:
                db_transaction = db.query(Transaction).filter(Transaction.transaction_id == removed["transaction_id"]).first()
                if db_transaction:
                    db_transaction.is_removed = True
                    db.merge(db_transaction)

            cursor = response["next_cursor"]
            if not response["has_more"]:
                logger.info("Transactions are completely fetched into database.")
                break

            time.sleep(1)
            request.cursor = cursor
            retry_count += 1
            if retry_count > max_retries:
                raise HTTPException(status_code=500, detail="Too many pages in sync response")

        if cursor_record:
            cursor.record.cursor = cursor
            cursor_record.updated_at = func.current_timestamp()
        else:
            db.add(SyncCursor(account_id=response["accounts"][0]["account_id"] if response.get("accounts") else "default_account", cursor=cursor))
        db.commit()

        logger.info(f"Sync completed: {len(processed_transactions)} transactions processed")
        return {"transactions": processed_transactions, "cursor": cursor}
    
    except Exception as e:
        handle_sync_error(e, access_token)
        db.rollback()
        raise
