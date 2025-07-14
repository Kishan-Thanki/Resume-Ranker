#!/bin/bash

# --- Load .env variables if running locally ---
# This block sources the .env file, making its variables available.
if [ -f .env ]; then
    export $(cat .env | xargs)
fi
# --- End .env loading ---

# Get FastAPI internal port from environment variable (from .env or Render dashboard)
# Use 8001 as a fallback if the variable is somehow not set
FASTAPI_INTERNAL_PORT=${FASTAPI_INTERNAL_PORT:-8001}

# Get the public port for Streamlit. Use Render's $PORT, then a local default (e.g., 8501).
PUBLIC_PORT=${PORT:-8501}

# Start FastAPI in the background on the internal port
# It's crucial for FastAPI to listen on 0.0.0.0 for internal communication
echo "Starting FastAPI on internal port ${FASTAPI_INTERNAL_PORT}..."
uvicorn app.main:app --host 0.0.0.0 --port "${FASTAPI_INTERNAL_PORT}" &

# Wait until FastAPI is available on its internal port
echo "Waiting for FastAPI to start on localhost:${FASTAPI_INTERNAL_PORT}..."
until curl -s http://localhost:${FASTAPI_INTERNAL_PORT}/docs > /dev/null; do
  sleep 1
done
echo "FastAPI is up and running on internal port ${FASTAPI_INTERNAL_PORT}."

# Start Streamlit, ensuring it binds to the Render-provided $PORT or local default
echo "Starting Streamlit on port ${PUBLIC_PORT}..."
streamlit run web/streamlit_app.py --server.port "${PUBLIC_PORT}" --server.enableCORS true --server.enableXsrfProtection false

# The Streamlit command will run in the foreground and keep the service alive.