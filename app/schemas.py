from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class JobDescriptionCreate(BaseModel):
    text: str = Field(min_length=50, max_length=10000, description="Detailed job description text. Extracted text content of the job description.")
    expires_at: datetime = Field(description="Date and Time (UTC) when the job description expires (Eligible for deletion).")

class JobDescriptionResponse(BaseModel):
    id: str = Field(description="An unique identifier for the job description.")
    text: str
    created_at: datetime = Field(description="Timestamp(UTC) when the job description was created.")

    model_config = {'from_attributes': True}

class ResumeCreate(BaseModel):
    filename: str = Field(min_length=3, max_length=255, description="Original filename of the resume (e.g., 'my_resume.pdf').")
    job_id: str = Field(pattern=r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", description="ID of the associated job description (UUID format).")
    text: str = Field(min_length=100, max_length=50000, description="Detailed Resume Text. Extracted text content of the resume.")
    expires_at: datetime = Field(description="Date and Time (UTC) when the resume expires (Eligible for deletion).")

    @field_validator('filename')
    @classmethod
    def filename_must_be_valid(cls, v: str):
        if '/' in v or '\\' in v:
            raise ValueError('Filename cannot contain path separators.')
        if '.' not in v or v.startswith('.'):
            raise ValueError('Filename must have a valid extension.')
        return v

class ResumeResponse(BaseModel):
    uuid: str
    job_id: str
    filename: str
    text: str
    created_at: datetime

    model_config = {'from_attributes': True}

class RankedResume(BaseModel):
    uuid: str
    filename: str
    score: float
