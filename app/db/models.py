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
    skills = Column(JSON, nullable=True)  
    experience = Column(JSON, nullable=True)  
    education = Column(JSON, nullable=True)  
    contact = Column(JSON, nullable=True)  
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)