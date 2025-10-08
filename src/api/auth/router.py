from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ...utils.auth import verify_password, create_access_token
from ...database.db import get_db
from ...models.account import Account
from ...schemas.account import Account as AccountSchema

router = APIRouter(prefix="/auth")

from pydantic import BaseModel
class LoginRequest(BaseModel):
    password: str

@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    if not verify_password(request.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    token, expires_at = create_access_token({"sub": "admin"})

    # Get all accounts from database
    accounts = db.query(Account).all()
    accounts_list = [AccountSchema.model_validate(account) for account in accounts]

    return {
        "token": token,
        "expires_at": expires_at.isoformat(),
        "accounts": accounts_list
    }