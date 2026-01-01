# app/schemas.py

from datetime import datetime
from pydantic import BaseModel, Field


class NotificationCreate(BaseModel):
    routing_key: str = Field(..., max_length=120)
    payload: str


class NotificationRead(BaseModel):
    id: int
    routing_key: str
    payload: str
    received_at: datetime

    class Config:
        from_attributes = True
