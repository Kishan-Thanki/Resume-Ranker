from app.database import Base
from sqlalchemy.sql import func
from sqlalchemy import Column, String, Text, ForeignKey, DateTime

class Job_Description(Base):
    __tablename__ = 'job_descriptions'

    id = Column(String, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Resume(Base):
    __tablename__ = 'resumes'

    uuid = Column(String, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("job_descriptions.id"), nullable=False)
    filename = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())