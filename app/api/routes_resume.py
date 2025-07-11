import os, uuid
from app import crud
from typing import List
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.utils.resume_parser import extract_text_resume
from fastapi import APIRouter, UploadFile, File, Form, Depends

router = APIRouter()

UPLOAD_FOLDER = 'app/static/uploads_resumes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post('/upload-resume/')
async def upload_resume(
        job_id: str = Form(...),
        resumes: List[UploadFile] = File(...),
        db: Session = Depends(get_db)
):
    parsed_resumes = []

    for file in resumes:
        resume_id = str(uuid.uuid4())
        file_name = f"{resume_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, file_name)

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        extracted_text = extract_text_resume(file_path)

        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Warning: failed to delete {file_path} — {e}")

        parsed_resumes.append({
            "uuid": resume_id,
            "filename": file.filename,
            "text": extracted_text.strip()
        })

    crud.insert_resumes(db, job_id, parsed_resumes)

    return {
        "message": "Resumes uploaded, parsed, and stored.",
        "count": len(parsed_resumes),
        "resumes": [r["filename"] for r in parsed_resumes]
    }
