from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from ...database.db import get_db
from ...models.account import Account
from ...models.transaction import Transaction
from ...models.sync_cursor import SyncCursor
from ...api.plaid.client import get_plaid_client
from ...utils.auth import verify_session_token
from ...config.settings import settings
from ...services.plaid import check_item_status
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transactions")
security = HTTPBearer()

def handle_sync_error(e, access_token: str):
    if hasattr(e, 'error_code'):
        if e.error_code == 'TRANSACTIONS_SYNC_LIMIT':
            logger.warning(f"Rate limit exceedded for /transactions/sync: {access_token[:10]}...")
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
        elif e.error_code == 'TRANSACTIONS_SYNC_MUTATION_DURING_PAGINATION':
            logger.warning(f"Pagination mutation during sync: Restarting loop for {access_token[:10]}...")
            raise HTTPException(status_code=500, detail="Sync interrupted. Restarting update.")
    raise HTTPException(status_code=500, detail=str(e))

@router.get("/sync")
async def sync_transactions(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    if not verify_session_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid session token")

    client = get_plaid_client()
    access_token = settings.PLAID_ACCESS_TOKEN

    # Check item status before syncing
    check_item_status(access_token)

    # cursor_record = db.query(SyncCursor).first()
    # cursor = cursor_record.cursor if cursor_record else ""
    cursor = ""
    request_num = 0

    added = []
    modified = []
    removed = []

    try:
        while True:
            request = TransactionsSyncRequest(
                access_token=access_token,
                cursor=cursor,
                count=500 # maximum txs to get once
            )
            response = client.transactions_sync(request)
            # print(response)
            # print("")

            added.extend(response["added"])
            modified.extend(response["modified"])
            removed.extend(response["removed"])

            cursor = response["next_cursor"]
            request_num += 1

            if not response["has_more"]:
                break

            if request_num > 3:
                break

        print(f"Added: {len(added)}, Modified: {len(modified)}, Removed: {len(removed)}")
        for tx in added:
            print(f"Date: {tx['date']}, Amount: {tx['amount']}, Desc: {tx['name']}")

        return {
            "added": added,
            "modified": modified,
            "removed": removed,
            "cursor": cursor
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))