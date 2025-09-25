from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CustomCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CustomCategoryCreate(CustomCategoryBase):
    pass

class CustomCategory(CustomCategoryBase):
    category_id: int
    created_at: datetime

    class Config:
        from_attributes = True