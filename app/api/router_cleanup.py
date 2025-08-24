from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from app.db.crud import cleanup_old_data
from app.db.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/cleanup/")
async def cleanup_expired_entries(db: Session = Depends(get_db)):
    current_time = datetime.now(timezone.utc)
    result = cleanup_old_data(db, current_time)

    return {"status": "cleanup complete", **result}