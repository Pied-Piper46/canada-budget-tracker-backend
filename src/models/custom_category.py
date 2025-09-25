from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from ..database.db import Base

class CustomCategory(Base):
    __tablename__ = "custom_categories"
    __table_args__ = {"schema": "cibc_budget_tracker_sandbox"}
    
    category_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())