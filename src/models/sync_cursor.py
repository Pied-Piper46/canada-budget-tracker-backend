from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database.db import Base
from ..config.settings import settings

class SyncCursor(Base):
    __tablename__ = "sync_cursors"
    __table_args__ = {"schema": settings.DATABASE_SCHEMA}

    account_id = Column(String(255), ForeignKey(f"{settings.DATABASE_SCHEMA}.accounts.account_id", ondelete="CASCADE"), primary_key=True)
    cursor = Column(String(255), nullable=False)
    updated_at = Column(DateTime, server_default=func.current_timestamp())