from sqlalchemy.orm import Session
from uuid import uuid4
from app.models import Job_Description, Resume

def insert_job_description(db: Session, text: str) -> str:
    job_id = str(uuid4())
    job = Job_Description(id=job_id, text=text)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job_id

def insert_resumes(db: Session, job_id: str, resumes: list[dict]) -> list[str]:
    resume_ids = []
    for res in resumes:
        resume = Resume(
            uuid=str(uuid4()),
            job_id=job_id,
            filename=res["filename"],
            text=res["text"]
        )
        db.add(resume)
        resume_ids.append(resume.uuid)
    db.commit()
    return resume_ids

def get_job_and_resumes(db: Session, job_id: str) -> tuple[str, list[dict]]:
    job = db.query(Job_Description).filter(Job_Description.id == job_id).first()
    if not job:
        return None, []

    resumes = db.query(Resume).filter(Resume.job_id == job_id).all()
    resume_list = [
        {
            "uuid": r.uuid,
            "filename": r.filename,
            "text": r.text
        }
        for r in resumes
    ]
    return job.text, resume_list
