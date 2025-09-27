from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AccountBase(BaseModel):
    account_id: str
    account_name: Optional[str]
    account_official_name: Optional[str]
    account_type: Optional[str]

class AccountCreate(AccountBase):
    pass

class Account(AccountBase):
    created_at: datetime
    last_synced_at: Optional[datetime] = None

    class Config:
        from_attributes = True