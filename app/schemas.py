from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class JobDescriptionCreate(BaseModel):
    text: str

class JobDescriptionResponse(BaseModel):
    id: str
    text: str
    created_at: datetime

    class Config:
        orm_mode = True

class ResumeCreate(BaseModel):
    filename: str
    text: str

class ResumeResponse(BaseModel):
    uuid: str
    job_id: str
    filename: str
    text: str
    created_at: datetime

    class Config:
        orm_mode = True

class RankedResume(BaseModel):
    uuid: str
    filename: str
    score: float
