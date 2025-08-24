import os
from dotenv import load_dotenv

# Loads the env into the application
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", default="http://localhost:8001")

DB_EXPIRY_HOURS = int(os.getenv("DB_EXPIRY_HOURS", 12))

MAX_RESUME_MB = int(os.getenv("MAX_RESUME_MB", default=3))
MAX_JOB_DESCRIPTION_MB = int(os.getenv("MAX_JOB_DESCRIPTION_MB", default=2))

ALLOWED_RESUME_MIME = os.getenv("ALLOWED_RESUME_MIME", default="application/pdf").split(",")
ALLOWED_JOB_DESCRIPTION_MIME = os.getenv("ALLOWED_JOB_DESCRIPTION_MIME", default="application/pdf, text/plain").split(",")