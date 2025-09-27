from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from ..database.db import Base
from ..config.settings import settings

class CustomCategory(Base):
    __tablename__ = "custom_categories"
    __table_args__ = {"schema": settings.DATABASE_SCHEMA}
    
    category_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())