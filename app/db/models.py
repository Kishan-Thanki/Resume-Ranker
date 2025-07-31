from sqlalchemy.sql import func
from app.db.database import Base
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, JSON

class Job_Description(Base):
    __tablename__ = 'job_descriptions'

    id = Column(String, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

class Resume(Base):
    __tablename__ = 'resumes'

    uuid = Column(String, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("job_descriptions.id"), nullable=False)
    filename = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    skills = Column(JSON, nullable=True)  # Store skills as JSON
    experience = Column(JSON, nullable=True)  # Store experience as JSON
    education = Column(JSON, nullable=True)  # Store education as JSON
    contact = Column(JSON, nullable=True)  # Store contact as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)