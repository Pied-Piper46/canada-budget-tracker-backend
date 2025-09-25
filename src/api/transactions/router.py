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

router = APIRouter(prefix="/transactions")
security = HTTPBearer()

@router.get("/sync")
async def sync_transactions(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    if not verify_session_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid session token")

    client = get_plaid_client()
    access_token = settings.PLAID_ACCESS_TOKEN
    cursor_record = db.query(SyncCursor).first()
    cursor = cursor_record.cursor if cursor_record else ""

    # Initialize an account for the first time
    # if not db.query(Account).first():
    #     db.add(Account(
    #         account_id="sandbox_account_1",
    #         institution_name="CIBC",
    #         account_name="Chequing",
    #         account_type="checking"
    #     ))
    #     db.commit()

    request = TransactionsSyncRequest(
        access_token=access_token,
        cursor=cursor
    )
    transactions = []

    try:
        while True:
            response = client.transactions_sync(request)
            for added in response["added"]:
                transactions.append(added.to_dict())

            if not response["has_more"]:
                break

        return {"transactions": transactions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))