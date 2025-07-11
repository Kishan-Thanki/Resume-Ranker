# Stage 1 — base image
FROM python:3.11-slim

# Set environment variables (non-interactive mode, production optimized)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENV=staging

# Set working directory
WORKDIR /app

# Install OS-level deps (optional but recommended for PDF parsing etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy files
COPY . /app

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Ensure the start.sh is executable
RUN chmod +x start.sh

# Expose FastAPI (8000) and Streamlit (8501) ports
EXPOSE 8000
EXPOSE 8501

# Run both services using bash
CMD ["./start.sh"]
