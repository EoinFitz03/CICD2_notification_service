# app/main.py

from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import NotificationDB
from app.schemas import NotificationCreate, NotificationRead

app = FastAPI(
    title="Notification Service API",
    description="Stores and exposes notifications created from RabbitMQ events",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/notifications", response_model=List[NotificationRead])
def list_notifications(db: Session = Depends(get_db)):
    return db.query(NotificationDB).order_by(NotificationDB.id.desc()).all()


@app.get("/notifications/{notification_id}", response_model=NotificationRead)
def get_notification(notification_id: int, db: Session = Depends(get_db)):
    n = db.query(NotificationDB).filter(NotificationDB.id == notification_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    return n


@app.post("/notifications", response_model=NotificationRead, status_code=status.HTTP_201_CREATED)
def create_notification(payload: NotificationCreate, db: Session = Depends(get_db)):
    n = NotificationDB(routing_key=payload.routing_key, payload=payload.payload)
    db.add(n)
    db.commit()
    db.refresh(n)
    return n
