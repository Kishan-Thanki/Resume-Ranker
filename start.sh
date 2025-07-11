#!/bin/bash

# Start FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Start Streamlit
streamlit run app/streamlit_app.py --server.port 8501 --server.enableCORS false
