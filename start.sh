#!/bin/bash

# Start FastAPI in background
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Wait until FastAPI is available
echo "Waiting for FastAPI to start..."
until curl -s http://localhost:8000/docs > /dev/null; do
  sleep 1
done

echo "FastAPI is up"

# Start Streamlit
streamlit run web/streamlit_app.py --server.port 8501 --server.enableCORS false
