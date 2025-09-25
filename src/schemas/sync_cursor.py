from pydantic import BaseModel
from datetime import datetime

class SyncCursorBase(BaseModel):
    account_id: str
    cursor: str

class SyncCursorCreate(SyncCursorBase):
    pass

class SyncCursor(SyncCursorBase):
    updated_at: datetime

    class Config:
        from_attributes = True