from fastapi import APIRouter, HTTPException
from ...utils.auth import verify_password, create_access_token

router = APIRouter(prefix="/auth")

from pydantic import BaseModel
class LoginRequest(BaseModel):
    password: str

@router.post("/login")
async def login(request: LoginRequest):
    if not verify_password(request.password):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    token, expires_at = create_access_token({"sub": "admin"})

    return {
        "token": token,
        "expires_at": expires_at.isoformat()
    }