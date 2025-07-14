import io
from app.db import crud
from typing import Optional
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from fastapi.responses import StreamingResponse

from app.schemas import JobDescriptionResponse
from app.utils.similarity import rank_resumes_by_similarity
from app.utils.job_description_parser import extract_text_job_file
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from app.utils.exports import generate_csv_ranked_resumes, generate_excel_from_ranked_data


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload-job-description/")
async def upload_job_description(
    job_text: Optional[str] = Form(None),
    job_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    if not job_text and not job_file:
        raise HTTPException(status_code=400, detail="Provide job_text or job_file.")

    job_content = job_text or extract_text_job_file(job_file)
    job_response: JobDescriptionResponse = crud.insert_job_description(db, job_content.strip())

    return {
        "message": "Job Description uploaded and stored.",
        "job_id": job_response.id,
        "text": job_response.text
    }

@router.post("/rank-resumes/")
async def rank_resumes(job_id: str = Form(...), db: Session = Depends(get_db)):
    job_text, resumes = crud.get_job_and_resumes(db, job_id)

    if not job_text:
        raise HTTPException(status_code=404, detail="Job Description not found.")
    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes found for this JD.")

    results = rank_resumes_by_similarity(job_text, resumes)

    return {
        "job_description_id": job_id,
        "total_resumes": len(results),
        "ranked_resumes": results
    }

@router.post("/download-ranked-resumes-csv/")
async def download_ranked_csv(job_id: str = Form(...), db: Session = Depends(get_db)):
    job_text, resumes = crud.get_job_and_resumes(db, job_id)
    if not job_text:
        raise HTTPException(status_code=404, detail="Job Description not found for download.")
    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes found to download for this JD.")

    ranked = rank_resumes_by_similarity(job_text, resumes)
    csv_bytes = generate_csv_ranked_resumes(ranked)

    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=ranked_resumes_{job_id}.csv"}
    )

@router.post("/download-ranked-resumes-excel/")
async def download_ranked_excel(job_id: str = Form(...), db: Session = Depends(get_db)):
    job_text, resumes = crud.get_job_and_resumes(db, job_id)
    if not job_text:
        raise HTTPException(status_code=404, detail="Job Description not found for download.")
    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes found to download for this JD.")

    ranked = rank_resumes_by_similarity(job_text, resumes)
    excel_bytes = generate_excel_from_ranked_data(ranked)

    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=ranked_resumes_{job_id}.xlsx"}
    )
