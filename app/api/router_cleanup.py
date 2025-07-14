from datetime import datetime
from sqlalchemy.orm import Session
from app.db.crud import cleanup_old_data
from app.db.database import SessionLocal
from fastapi import APIRouter, Depends, Body

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/cleanup/")
async def cleanup_expired_entries(current_time: dict = Body(...), db: Session = Depends(get_db)):
    try:
        dt = datetime.fromisoformat(current_time["current_time"])
    except (KeyError, ValueError):
        return {"error": "Invalid or missing datetime. Expected ISO 8601 format under key 'current_time'."}

    result = cleanup_old_data(db, dt)
    return {"status": "cleanup complete", **result}