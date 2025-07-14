import os
import requests
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8001")

MAX_RESUME_MB = int(os.getenv("MAX_RESUME_MB", 3))
MAX_JOB_DESCRIPTION_FILE_MB = int(os.getenv("MAX_JOB_DESCRIPTION_MB", 2))

def file_too_large(file_obj, max_mb):
    return len(file_obj.getvalue()) > max_mb * 1024 * 1024

try:
    resp = requests.post(f"{FASTAPI_BASE_URL}/clean/cleanup/", json={"current_time": datetime.now(timezone.utc).isoformat()})
    if resp.ok:
        print("DB Cleanup succeeded")
    else:
        st.warning("Cleanup API responded but failed")
except requests.exceptions.ConnectionError:
    st.warning("Cleanup failed: Backend not running")


# Configure page
layout="centered"
st.set_page_config(
    page_title="Resume Ranker",
    layout=layout,
)

# Custom CSS styling
st.markdown("""
<style>
    .header {
        padding: 1rem 0 0.5rem;
        border-bottom: 1px solid #e0e0e0;
        margin-bottom: 2rem;
    }
    .step-card {
        background-color: #f8fafc;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .step-title {
        color: #1e40af;
        margin-bottom: 1rem !important;
    }
    .btn-primary {
        background-color: #2563eb !important;
        color: white !important;
        border: none !important;
    }
    .btn-primary:hover {
        background-color: #1d4ed8 !important;
    }
    .success-box {
        background-color: #dcfce7;
        border-left: 4px solid #22c55e;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    .file-info {
        background-color: #f1f5f9;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #cbd5e1, transparent);
        margin: 1.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="header">
    <h1 style='font-size: 2.4rem; font-weight: 700; margin-bottom: 0.4rem; color: #1e293b;'>
        Resume Ranker AI
    </h1>
    <p style='font-size: 1.1rem; color: #475569; margin-bottom: 0.5rem;'>
        Upload a Job Description and multiple resumes. Get AI-powered ranking and insights.
    </p>
</div>
""", unsafe_allow_html=True)

# Status indicators
if 'job_id' in st.session_state:
    st.markdown(f"""
    <div class="success-box">
        <div style="display: flex; align-items: center; gap: 10px;">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
            <div>
                <strong>Job Description Uploaded</strong>
                <div style="font-size: 0.9rem; margin-top: 4px;">ID: {st.session_state.job_id}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if 'resume_count' in st.session_state:
    st.markdown(f"""
    <div class="success-box">
        <div style="display: flex; align-items: center; gap: 10px;">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            <div>
                <strong>Resumes Uploaded</strong>
                <div style="font-size: 0.9rem; margin-top: 4px;">{st.session_state.resume_count} resumes ready for ranking</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# === Step 1: Upload Job Description ===
st.markdown("""
<div class="step-card">
    <h3 class="step-title">Step 1: Upload Job Description</h3>
    <div style="margin-bottom: 1rem;">
        <p style="color: #4b5563; margin-bottom: 1rem;">
            Start by providing the job description either by pasting text or uploading a file.
        </p>
        <div class="stAlert" style="margin-bottom: 1.5rem;">
            <div class="warning-box">
                <div style="display: flex; align-items: flex-start; gap: 10px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <div>PDF files may take longer to process</div>
                </div>
            </div>
        </div>
""", unsafe_allow_html=True)

if layout == "centered":
    height = 130
elif layout == "wide":
    height = 75

col1, col2 = st.columns([1, 1], gap="large")
with col1:
    job_text = st.text_area("**Paste Job Description (Text):**",
                            height=height,
                            placeholder="Enter job title, requirements, responsibilities...")
with col2:
    job_file = st.file_uploader(
        "**Upload Job Description (File - Max 2MB):**",
        type=["txt", "pdf"],
        accept_multiple_files=False,
        help="Accepted formats: .txt and .pdf (Max size: 2MB)"
    )

st.markdown("</div>", unsafe_allow_html=True)  # Close step-card

if st.button("Upload Job Description", key="jd_upload", use_container_width=True):
    if not job_text and not job_file:
        st.markdown("""
        <div class="warning-box">
            <div style="display: flex; align-items: flex-start; gap: 10px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                <div>Please provide either job description text or upload a file</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        data, files = {}, None
        if job_text:
            data["job_text"] = job_text
        if job_file:
            if file_too_large(job_file, MAX_JOB_DESCRIPTION_FILE_MB):
                st.error(f"Job description file exceeds {MAX_JOB_DESCRIPTION_FILE_MB} MB limit.")
                job_file = None
            else:
                files = {"job_file": (job_file.name, job_file, job_file.type or "application/pdf")}

        with st.spinner("Processing job description..."):
            try:
                # --- MODIFIED HERE ---
                resp = requests.post(f"{FASTAPI_BASE_URL}/ranker/upload-job-description/", data=data, files=files)
                # --- END MODIFIED ---
            except Exception as e:
                st.error(f"Connection error: {e}")
                resp = None

        if resp and resp.ok:
            job_id = resp.json().get("job_id")
            st.session_state["job_id"] = job_id
            if 'resume_count' in st.session_state:
                del st.session_state['resume_count']  # Reset resumes if JD changes
            st.success("Job description uploaded successfully")
        elif resp:
            st.error(resp.json().get("detail", "Job description upload failed"))

# Divider
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# === Step 2: Upload Resumes ===
st.markdown("""
<div class="step-card">
    <h3 class="step-title">Step 2: Upload Resumes</h3>
    <p style="color: #4b5563; margin-bottom: 1.5rem;">
        Upload candidate resumes in PDF format. Multiple files can be selected.
    </p>
""", unsafe_allow_html=True)

resume_files = st.file_uploader("**Select Resume Files (PDF):**",
                                type="pdf",
                                accept_multiple_files=True,
                                help="Only PDF files are accepted for resumes")

oversized_files = [f.name for f in resume_files if file_too_large(f, MAX_RESUME_MB)]

if oversized_files:
    st.warning(f"The following resume(s) exceed {MAX_RESUME_MB} MB limit and will be skipped:\n\n" +
               "\n".join(f"- {name}" for name in oversized_files))

    # Filter out large files before upload
    resume_files = [f for f in resume_files if not file_too_large(f, MAX_RESUME_MB)]


if resume_files:
    st.markdown("<div style='margin-top: -15px; margin-bottom: 15px;'>", unsafe_allow_html=True)
    for i, f in enumerate(resume_files):
        st.markdown(f"""
        <div class="file-info">
            <div style="display: flex; align-items: center; gap: 8px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
                    <polyline points="13 2 13 9 20 9"></polyline>
                </svg>
                <span>{f.name}</span>
                <span style="margin-left: auto; font-size: 0.85rem; color: #94a3b8;">{round(len(f.getvalue()) / 1024, 1)} KB</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # Close inner content
    st.markdown("</div>", unsafe_allow_html=True)  # Close step-card

    if st.button("Upload Resumes", key="resume_upload", use_container_width=True):
        job_id = st.session_state.get("job_id")

        if not job_id:
            st.markdown("""
            <div class="warning-box">
                <div style="display: flex; align-items: flex-start; gap: 10px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <div>Please upload a job description first</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif not resume_files:
            st.markdown("""
            <div class="warning-box">
                <div style="display: flex; align-items: flex-start; gap: 10px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <div>Please select at least one resume file to upload</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            files = [("resumes", (f.name, f, "application/pdf")) for f in resume_files]
            with st.spinner(f"Uploading {len(resume_files)} resumes..."):
                try:
                    # --- MODIFIED HERE ---
                    resp = requests.post(f"{FASTAPI_BASE_URL}/resumes/upload-resume/", data={"job_id": job_id}, files=files)
                    # --- END MODIFIED ---
                except Exception as e:
                    st.error(f"Connection error: {e}")
                    resp = None

            if resp and resp.ok:
                count = resp.json().get("count", 0)
                st.session_state["resume_count"] = count
                st.success(f"{count} resume(s) processed successfully")
            elif resp:
                st.error(resp.json().get("detail", "Resume upload failed"))

    # Divider
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # === Step 3: Rank Resumes ===
    st.markdown("""
    <div class="step-card">
        <h3 class="step-title">Step 3: Rank Resumes</h3>
        <p style="color: #4b5563; margin-bottom: 1.5rem;">
            Generate AI-powered ranking and insights for candidate resumes.
        </p>
    """, unsafe_allow_html=True)

    if st.button("Rank Resumes", key="ranking", use_container_width=True):
        job_id = st.session_state.get("job_id")
        resume_count = st.session_state.get("resume_count", 0)

        if not job_id:
            st.markdown("""
            <div class="warning-box">
                <div style="display: flex; align-items: flex-start; gap: 10px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
                         viewBox="0 0 24 24" fill="none" stroke="#f59e0b"
                         stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <div>Please complete Step 1 first</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif resume_count == 0:
            st.markdown("""
            <div class="warning-box">
                <div style="display: flex; align-items: flex-start; gap: 10px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
                         viewBox="0 0 24 24" fill="none" stroke="#f59e0b"
                         stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <div>Please upload resumes in Step 2</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            with st.spinner("Analyzing and ranking resumes..."):
                try:
                    # --- MODIFIED HERE ---
                    resp = requests.post(f"{FASTAPI_BASE_URL}/ranker/rank-resumes/", data={"job_id": job_id})
                    # --- END MODIFIED ---
                except Exception as e:
                    st.error(f"Connection error: {e}")
                    resp = None

            if resp and resp.ok:
                ranked = resp.json().get("ranked_resumes", [])

                if ranked:
                    st.success(f"Successfully ranked {len(ranked)} resumes")

                    st.subheader("Top Candidates")
                    cols = st.columns(3)

                    for i, candidate in enumerate(ranked[:3]):
                        with cols[i]:
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #eff6ff, #dbeafe);
                                        border-radius: 12px; padding: 1.5rem; text-align: center;
                                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
                                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">#{i + 1}</div>
                                <div title="{candidate.get('filename')}" style=" font-weight: 600; font-size: 1.1rem; margin-bottom: 1rem; word-wrap: break-word; overflow-wrap: break-word; text-align: center; max-width: 100%; white-content: nowrap; overflow: hidden; text-overflow: ellipsis; ">
                                    {candidate.get('candidate_name') or candidate.get('filename') or 'Candidate ' + str(i + 1)}
                                </div>
                                <div style="display: flex; flex-direction: column; gap: 8px;">
                                    <div style="background-color: white; border-radius: 8px; padding: 8px;">
                                        <div style="font-size: 0.9rem; color: #64748b;">Overall Score</div>
                                        <div style="font-size: 1.4rem; font-weight: 700; color: #1e40af;">
                                            {candidate['score']:.1f}%
                                        </div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                    # Show full results
                    st.subheader("Ranking Results")
                    st.dataframe(ranked, use_container_width=True, height=400)

                    # Download options
                    st.subheader("Export Results")
                    dl_col1, dl_col2 = st.columns(2)

                    with dl_col1:
                        st.download_button(
                            label="Download as CSV",
                            data=requests.post(f"{FASTAPI_BASE_URL}/ranker/download-ranked-resumes-csv/",
                                               data={"job_id": job_id}).content,
                            file_name="ranked_resumes.csv",
                            mime="text/csv"
                        )
                    with dl_col2:
                        st.download_button(
                            label="Download as Excel",
                            data=requests.post(f"{FASTAPI_BASE_URL}/ranker/download-ranked-resumes-excel/",
                                               data={"job_id": job_id}).content,
                            file_name="ranked_resumes.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.warning("No ranked results returned")
            elif resp:
                st.error(resp.json().get("detail", "Ranking failed"))

    # Close Step 3 card
    st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div style="margin-top: 4rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; text-align: center; color: #64748b; font-size: 0.9rem;">
        <div>Resume Ranker AI • Automated Candidate Evaluation System</div>
        <div style="margin-top: 0.5rem;">v1.0.0</div>
    </div>
    """, unsafe_allow_html=True)