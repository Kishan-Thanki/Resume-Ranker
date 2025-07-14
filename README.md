# Resume Ranker

**Resume Shortlisting Tool**

## Overview
Resume Ranker is a lightweight ATS-style system that allows users to upload a job description and multiple resumes. It then ranks the resumes using scoring logic based on relevance.

## Tech Stack
- Frontend: Streamlit
- Backend: FastAPI
- File Uploads: PDF/Text
- Output: CSV, Excel Download
- Future Plans: ML-based Ranking (NLP-based)

## Features
- Upload Job Description (Text or File)
- Upload Multiple Resumes (PDF)
- Rank Candidates by Score
- View & Download Results

## Project Structure
```
resume-ranker
├── app/
    ├── api/
    ├── db/
    ├── static/
    ├── utils/
    ├── __init__.py
    ├── main.py
    ├── schemas.py
├── web
    ├── steamlit_app.py
├── .gitignore
├── config.py
├── README.md
├── requirements.txt
|__ start.sh
```

---

Note: This is a demo project. Not production-ready.
