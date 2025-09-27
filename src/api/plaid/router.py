from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from sqlalchemy.orm import Session
from ...database.db import get_db
from ...models.account import Account
from .client import get_plaid_client
from ...utils.auth import verify_session_token

router = APIRouter(prefix="/plaid")
security = HTTPBearer()

from pydantic import BaseModel
class PublicTokenExchangeRequest(BaseModel):
    public_token: str

@router.post("/link/token/create")
async def create_link_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not verify_session_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid session token")
    client = get_plaid_client()
    request = LinkTokenCreateRequest(
        user={"client_user_id": "user_1"},
        client_name="CIBC Budget Tracker",
        products=[Products("transactions")],
        country_codes=[CountryCode("CA")],
        language="en",
    )
    try:
        response = client.link_token_create(request)
        return {"link_token": response["link_token"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/item/public_token/exchange")
async def exchange_public_token(request: PublicTokenExchangeRequest, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    if not verify_session_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid session token")
    client = get_plaid_client()
    request = ItemPublicTokenExchangeRequest(public_token=request.public_token)
    try:
        response = client.item_public_token_exchange(request)
        access_token = response["access_token"]
        item_id = response["item_id"]
        print(access_token)

        accounts_request = AccountsGetRequest(access_token=access_token)
        accounts_response = client.accounts_get(accounts_request)
        print(accounts_response)
        for account in accounts_response["accounts"]:
            db_account = Account(
                account_id=account["account_id"],
                institution_name="CIBC",
                account_name=account["name"],
                account_type=str(account["type"])
            )
            db.merge(db_account)
        db.commit()
        # with open(".env", "a") as f:
        #     f.write(f"\nPLAID_ACCESS_TOKEN={access_token}\nPLAID_ITEM_ID={item_id}")
        return {"status": "success", "access_token": access_token, "item_id": item_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))