import os
import uuid
from typing import List
from app.db import crud
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.utils.resume_parser import ResumeParser
from fastapi import APIRouter, UploadFile, Form, Depends, HTTPException

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
async def upload_resume(job_id: str = Form(...), resumes: List[UploadFile] = Form(...), db: Session = Depends(get_db)):
    parsed_resumes = []
    failed_uploads = []
    resume_filenames = []

    parser = ResumeParser()

    for file in resumes:
        resume_id = str(uuid.uuid4())
        file_name = f"{resume_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, file_name)

        try:
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())

            enhanced_data = parser.parse_resume(file_path)
            parsed_resumes.append({
                "uuid": resume_id,
                "filename": file.filename,
                "text": enhanced_data.get('raw_text', '').strip(),
                "skills": enhanced_data.get('skills', []),
                "experience": enhanced_data.get('experience', []),
                "education": enhanced_data.get('education', []),
                "contact": enhanced_data.get('contact', {})
            })
        except Exception as e:
            print(f"Error processing resume {file.filename}: {e}")
            failed_uploads.append(file.filename)
        finally:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Warning: failed to delete temporary file {file_path} — {e}")

    if parsed_resumes:
        try:
            crud.insert_resumes(db, job_id, parsed_resumes)
        except Exception as e:
            print(f"Database error while storing resumes: {e}")
            raise HTTPException(status_code=500, detail="An error occurred while storing resumes.")
    else:
        if failed_uploads:
            raise HTTPException(status_code=400, detail=f"No resumes could be processed. Failed: {', '.join(failed_uploads)}")
        else:
            raise HTTPException(status_code=400, detail="No resumes provided or no valid resumes could be processed.")

    response_message = "Resumes uploaded, parsed, and stored."
    if failed_uploads:
        response_message += f" However, the following resumes failed to process: {', '.join(failed_uploads)}."

    for r in parsed_resumes:
        resume_filenames.append(r["filename"])

    return {
        "message": response_message,
        "count": len(parsed_resumes),
        "resumes": resume_filenames,
        "failed_resumes": failed_uploads
    }