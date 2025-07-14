import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# create_engine is used to talk to DB and handle connections
engine = create_engine(config.DATABASE_URL, pool_pre_ping=True)

# Create a factory for database sessions, which performs common operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model
Base = declarative_base()