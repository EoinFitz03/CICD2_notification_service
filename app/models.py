# app/models.py

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

from app.database import engine

Base = declarative_base()


class NotificationDB(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    routing_key = Column(String(120), nullable=False, index=True)
    payload = Column(Text, nullable=False)  # JSON stored as text
    received_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# Create tables when imported by API/worker
Base.metadata.create_all(bind=engine)
