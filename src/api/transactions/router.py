from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from plaid.model.item_get_request import ItemGetRequest
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

    item_request = ItemGetRequest(access_token=access_token)
    try:
        item_response = client.item_get(item_request)
        # item_status = item_response["item"]["status"]
        if item_response["item"].get("error"):
            raise HTTPException(status_code=400, detail="Item login required. Please re-authenticate via Plaid Link update mode.")
    except Exception as e:
        if hasattr(e, 'error_code') and e.error_code == 'ITEM_LOGIN_REQUIRED':
            raise HTTPException(status_code=400, detail="Item login required. Please re-authenticate via Plaid Link update mode.")
        raise HTTPException(status_code=500, detail=str(e))


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
            modified.extend(response(["modified"]))
            removed.extend(response["removed"])

            cursor = response["next_cursor"]
            request_num += 1

            if not response["has_more"]:
                break

            if request_num > 3:
                break

        return {"transactions": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))