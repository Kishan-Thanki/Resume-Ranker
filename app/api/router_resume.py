import os, uuid



from app.db import crud
from typing import List
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.utils.resume_parser import extract_text_resume
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException

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
    failed_uploads = []

    for file in resumes:
        resume_id = str(uuid.uuid4())
        file_name = f"{resume_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, file_name)

        try:
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())

            extracted_text = extract_text_resume(file_path)
            parsed_resumes.append({
                "uuid": resume_id,
                "filename": file.filename,
                "text": extracted_text.strip()
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
        except IntegrityError:
            raise HTTPException(status_code=409, detail="A database conflict occurred during resume storage. Please try again.")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error while storing resumes: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred while storing resumes: {e}")
    else:
        if failed_uploads:
            raise HTTPException(status_code=400, detail=f"No resumes could be processed successfully. Failed: {', '.join(failed_uploads)}")
        else:
            raise HTTPException(status_code=400, detail="No resumes provided or no valid resumes could be processed.")

    response_message = "Resumes uploaded, parsed, and stored."
    if failed_uploads:
        response_message += f" However, the following resumes failed to process: {', '.join(failed_uploads)}."

    return {
        "message": response_message,
        "count": len(parsed_resumes),
        "resumes": [r["filename"] for r in parsed_resumes],
        "failed_resumes": failed_uploads
    }