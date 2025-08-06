#!/bin/bash

# Load .env variables if the file exists
[ -f .env ] && export $(cat .env | xargs)

# Set ports
FASTAPI_INTERNAL_PORT=${FASTAPI_INTERNAL_PORT:-8001}
PUBLIC_PORT=${PORT:-8501}

# Start FastAPI in background
echo "Starting FastAPI on port ${FASTAPI_INTERNAL_PORT}..."
uvicorn app.main:app --host 0.0.0.0 --port "${FASTAPI_INTERNAL_PORT}" &

# Wait for FastAPI to be ready
echo "Waiting for FastAPI to be ready..."
until curl -s http://localhost:${FASTAPI_INTERNAL_PORT}/docs > /dev/null; do
  sleep 1
done

# Start Streamlit
echo "Starting Streamlit on port ${PUBLIC_PORT}..."
streamlit run web/streamlit_app.py --server.port "${PUBLIC_PORT}" --server.enableCORS true --server.enableXsrfProtection false