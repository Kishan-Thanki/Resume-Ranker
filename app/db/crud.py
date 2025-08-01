import config
from uuid import uuid4
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.db.models import Job_Description, Resume
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.schemas import JobDescriptionCreate, JobDescriptionResponse, ResumeCreate, ResumeResponse

EXPIRY_HOURS = config.DB_EXPIRY_HOURS

def insert_job_description(db: Session, job_text: str) -> JobDescriptionResponse:
    try:
        job_id = str(uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(hours=EXPIRY_HOURS)

        job = Job_Description(id=job_id, text=job_text, expires_at=expires_at)
        db.add(job)
        db.commit()
        db.refresh(job)

        return JobDescriptionResponse.model_validate(job)
    except SQLAlchemyError as e:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise

def insert_resumes(db: Session, job_id: str, resumes: List[dict]) -> List[str]:
    resume_ids = []

    try:
        if not resumes:
            return []

        expires_at = datetime.now(timezone.utc) + timedelta(hours=EXPIRY_HOURS)

        for res in resumes:
            resume = Resume(
                uuid=res["uuid"],
                job_id=job_id,
                filename=res["filename"],
                text=res["text"],
                skills=res.get("skills", {}),
                experience=res.get("experience", {}),
                education=res.get("education", {}),
                contact=res.get("contact", {}),
                expires_at=expires_at
            )
            db.add(resume)
            resume_ids.append(res["uuid"])

        db.commit()

        return resume_ids
    except Exception as e:
        db.rollback()
        print(f"Unexpected error in insert_resumes for job_id {job_id}: {e}")
        raise

def get_job_and_resumes(db: Session, job_id: str) -> tuple[str, list[dict]]:
    # Query the Job_Description Model based on the job_id and returns the first one found
    job = db.query(Job_Description).filter(Job_Description.id == job_id).first()
    if not job:
        return "", []

    # If job_id found, it gets all the related resume from Resume Model based on the job_id
    resumes = db.query(Resume).filter(Resume.job_id == job_id).all()
    resume_list = [
        {
            "uuid": r.uuid,
            "filename": r.filename,
            "text": r.text,
            "skills": r.skills or {},
            "experience": r.experience or {},
            "education": r.education or {},
            "contact": r.contact or {}
        }
        for r in resumes
    ]

    return job.text, resume_list

def cleanup_old_data(db: Session, current_time: datetime) -> dict:
    deleted_resumes = db.query(Resume).filter(Resume.expires_at <= current_time).delete()
    deleted_jobs = db.query(Job_Description).filter(Job_Description.expires_at <= current_time).delete()
    db.commit()
    return {
        "deleted_job_descriptions": deleted_jobs,
        "deleted_resumes": deleted_resumes
    }