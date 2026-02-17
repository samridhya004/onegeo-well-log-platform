from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class Well(Base):
    __tablename__ = "wells"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
