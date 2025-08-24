import os
import requests
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime, timezone

# --- Configuration & Initialization ---
load_dotenv()
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")
MAX_RESUME_MB = int(os.getenv("MAX_RESUME_MB", 3))
MAX_JOB_DESCRIPTION_FILE_MB = int(os.getenv("MAX_JOB_DESCRIPTION_MB", 2))


# --- Helper Functions ---
def file_too_large(file_obj, max_mb):
    return len(file_obj.getvalue()) > max_mb * 1024 * 1024


def call_api(endpoint, method="POST", data=None, files=None):
    """A centralized function to handle all API calls."""
    # This is the line that was causing the error - it was adding the base URL again.
    # The fix is to ensure the endpoint passed into this function does not include the base URL.
    full_url = f"{FASTAPI_BASE_URL}{endpoint}"
    try:
        if method.upper() == "POST":
            resp = requests.post(full_url, data=data, files=files)
        elif method.upper() == "GET":
            # For GET requests, data should be passed as params
            resp = requests.get(full_url, params=data)
        else:
            raise ValueError("Unsupported HTTP method")

        return resp
    except requests.exceptions.ConnectionError:
        st.error(f"Connection error: The backend is not running at {FASTAPI_BASE_URL}.")
        return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None


def show_message_box(message, type="success", icon=None):
    """Displays a stylized success or warning message."""
    box_styles = {
        "success": {"bg": "#dcfce7", "border": "#22c55e", "icon": "✅"},
        "warning": {"bg": "#fffbeb", "border": "#f59e0b", "icon": "⚠️"},
        "error": {"bg": "#fef2f2", "border": "#ef4444", "icon": "❌"}
    }
    style = box_styles.get(type, box_styles["success"])
    icon_svg = icon or style["icon"]
    st.markdown(
        f"""
        <div style="background-color: {style['bg']}; border-left: 4px solid {style['border']}; padding: 1rem; border-radius: 0 8px 8px 0; margin: 1rem 0;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.5rem;">{icon_svg}</span>
                <div>{message}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# --- Initial API Call (can be removed if not needed) ---
try:
    resp = call_api("/clean/cleanup/", data={"current_time": datetime.now(timezone.utc).isoformat()})
    if resp and resp.ok:
        print("DB Cleanup succeeded")
    else:
        st.warning("Cleanup API responded but failed or backend not running")
except Exception:
    st.warning("Cleanup failed: Backend not running or check the API endpoint")

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Resume Ranker", layout="centered")

# Custom CSS styling
st.markdown("""
<style>
    .header { padding: 1rem 0 0.5rem; border-bottom: 1px solid #e0e0e0; margin-bottom: 2rem; }
    .step-card { background-color: #f8fafc; border-radius: 10px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .step-title { color: #1e40af; margin-bottom: 1rem !important; }
    .btn-primary { background-color: #2563eb !important; color: white !important; border: none !important; }
    .btn-primary:hover { background-color: #1d4ed8 !important; }
    .file-info { background-color: #f1f5f9; padding: 0.5rem 1rem; border-radius: 6px; margin: 0.5rem 0; font-size: 0.9rem; }
    .divider { height: 1px; background: linear-gradient(90deg, transparent, #cbd5e1, transparent); margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="header">
    <h1 style='font-size: 2.4rem; font-weight: 700; margin-bottom: 0.4rem; color: #1e293b;'>Resume Ranker</h1>
    <p style='font-size: 1.1rem; color: #475569; margin-bottom: 0.5rem;'>
        Upload a Job Description and multiple resumes. Get AI-powered ranking and insights.
    </p>
</div>
""", unsafe_allow_html=True)

# Status indicators
if 'job_id' in st.session_state:
    show_message_box(
        f"<strong>Job Description Uploaded</strong><div style='font-size: 0.9rem; margin-top: 4px;'>ID: {st.session_state.job_id}</div>"
    )

if 'resume_count' in st.session_state:
    show_message_box(
        f"<strong>Resumes Uploaded</strong><div style='font-size: 0.9rem; margin-top: 4px;'>{st.session_state.resume_count} resumes ready for ranking</div>"
    )

# === Step 1: Upload Job Description ===
st.markdown("""
<div class="step-card">
    <h3 class="step-title">Step 1: Upload Job Description</h3>
    <p style="color: #4b5563; margin-bottom: 1rem;">
        Start by providing the job description either by pasting text or uploading a file.
    </p>
    """, unsafe_allow_html=True)

st.warning(f"PDF files may take longer to process. Max size: {MAX_JOB_DESCRIPTION_FILE_MB}MB")

col1, col2 = st.columns([1, 1], gap="large")
with col1:
    job_text = st.text_area("**Paste Job Description (Text):**", height=130,
                            placeholder="Enter job title, requirements, responsibilities...")
with col2:
    job_file = st.file_uploader(
        "**Upload Job Description (File):**",
        type=["txt", "docx"],
        accept_multiple_files=False,
    )

if st.button("Upload Job Description", key="jd_upload", use_container_width=True):
    if not job_text and not job_file:
        show_message_box("Please provide either job description text or upload a file", "warning")
    else:
        data, files = {}, None
        if job_text:
            data["job_text"] = job_text
        if job_file:
            if file_too_large(job_file, MAX_JOB_DESCRIPTION_FILE_MB):
                st.error(f"Job description file exceeds {MAX_JOB_DESCRIPTION_FILE_MB} MB limit.")
                job_file = None
            else:
                files = {"job_file": (job_file.name, job_file.getvalue(), job_file.type or "application/pdf")}

        with st.spinner("Processing job description..."):
            resp = call_api("/ranker/upload-job-description/", data=data, files=files)

        if resp and resp.ok:
            job_id = resp.json().get("job_id")
            st.session_state["job_id"] = job_id
            if 'resume_count' in st.session_state:
                del st.session_state['resume_count']
            show_message_box("Job description uploaded successfully", "success")
        elif resp:
            show_message_box(resp.json().get("detail", "Job description upload failed"), "error")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# === Step 2: Upload Resumes ===
st.markdown("""
<div class="step-card">
    <h3 class="step-title">Step 2: Upload Resumes</h3>
    <p style="color: #4b5563; margin-bottom: 1.5rem;">
        Upload candidate resumes in PDF format. Multiple files can be selected.
    </p>
""", unsafe_allow_html=True)

resume_files = st.file_uploader(
    "**Select Resume Files (PDF):**",
    type="pdf",
    accept_multiple_files=True,
    help=f"Only PDF files are accepted. Max size: {MAX_RESUME_MB}MB per file."
)

if resume_files:
    oversized_files = [f.name for f in resume_files if file_too_large(f, MAX_RESUME_MB)]
    if oversized_files:
        st.warning(f"The following resume(s) exceed {MAX_RESUME_MB} MB limit and will be skipped:\n\n" +
                   "\n".join(f"- {name}" for name in oversized_files))
        resume_files = [f for f in resume_files if not file_too_large(f, MAX_RESUME_MB)]

    if resume_files:
        st.info(f"{len(resume_files)} file(s) ready to upload.")

    if st.button("Upload Resumes", key="resume_upload", use_container_width=True):
        job_id = st.session_state.get("job_id")
        if not job_id:
            show_message_box("Please complete Step 1 first", "warning")
        elif not resume_files:
            show_message_box("Please select at least one resume file to upload", "warning")
        else:
            files = [("resumes", (f.name, f.getvalue(), "application/pdf")) for f in resume_files]
            with st.spinner(f"Uploading {len(resume_files)} resumes..."):
                resp = call_api("/resumes/upload-resume/", data={"job_id": job_id}, files=files)
            if resp and resp.ok:
                count = resp.json().get("count", 0)
                st.session_state["resume_count"] = count
                show_message_box(f"{count} resume(s) processed successfully", "success")
            elif resp:
                show_message_box(resp.json().get("detail", "Resume upload failed"), "error")

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
        show_message_box("Please complete Step 1 first", "warning")
    elif resume_count == 0:
        show_message_box("Please upload resumes in Step 2", "warning")
    else:
        with st.spinner("Analyzing and ranking resumes..."):
            resp = call_api("/ranker/rank-resumes/", data={"job_id": job_id})

        if resp and resp.ok:
            ranked = resp.json().get("ranked_resumes", [])
            if ranked:
                st.session_state["ranked_resumes"] = ranked  # Save ranked data to session state
                show_message_box(f"Successfully ranked {len(ranked)} resumes", "success")
                st.subheader("Top Candidates")
                cols = st.columns(3)
                for i, candidate in enumerate(ranked[:3]):
                    with cols[i]:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #eff6ff, #dbeafe); border-radius: 12px; padding: 1.5rem; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
                            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">#{i + 1}</div>
                            <div title="{candidate.get('filename')}" style="font-weight: 600; font-size: 1.1rem; margin-bottom: 1rem; word-wrap: break-word; overflow-wrap: break-word; text-align: center; max-width: 100%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                {candidate.get('candidate_name') or candidate.get('filename') or 'Candidate ' + str(i + 1)}
                            </div>
                            <div style="display: flex; flex-direction: column; gap: 8px;">
                                <div style="background-color: white; border-radius: 8px; padding: 8px;">
                                    <div style="font-size: 0.9rem; color: #64748b;">Overall Score</div>
                                    <div style="font-size: 1.4rem; font-weight: 700; color: #1e40af;">
                                        {candidate.get('combined_score', candidate.get('score', 0)):.1f}%
                                    </div>
                                </div>
                                <div style="background-color: white; border-radius: 8px; padding: 8px;">
                                    <div style="font-size: 0.8rem; color: #64748b;">Skills Score</div>
                                    <div style="font-size: 1.1rem; font-weight: 600; color: #059669;">
                                        {candidate.get('skill_score', 0):.1f}%
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                st.subheader("Ranking Results")
                st.dataframe(ranked, use_container_width=True, height=400)

                st.subheader("Export Results")
                dl_col1, dl_col2 = st.columns(2)

                with dl_col1:
                    download_csv_endpoint = "/ranker/download-ranked-resumes-csv/"
                    with st.spinner("Preparing CSV..."):
                        csv_resp = call_api(download_csv_endpoint, method="POST", data={"job_id": job_id})
                    if csv_resp and csv_resp.ok:
                        st.download_button(
                            label="Download as CSV",
                            data=csv_resp.content,
                            file_name="ranked_resumes.csv",
                            mime="text/csv"
                        )
                with dl_col2:
                    download_excel_endpoint = "/ranker/download-ranked-resumes-excel/"
                    with st.spinner("Preparing Excel..."):
                        excel_resp = call_api(download_excel_endpoint, method="POST", data={"job_id": job_id})
                    if excel_resp and excel_resp.ok:
                        st.download_button(
                            label="Download as Excel",
                            data=excel_resp.content,
                            file_name="ranked_resumes.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
            else:
                show_message_box("No ranked results returned", "warning")
        elif resp:
            show_message_box(resp.json().get("detail", "Ranking failed"), "error")

# Close Step 3 card
st.markdown("</div>", unsafe_allow_html=True)

# === Step 4: Detailed Analysis ===
if 'ranked_resumes' in st.session_state and st.session_state['ranked_resumes']:
    st.markdown("""
    <div class="step-card">
        <h3 class="step-title">Step 4: Detailed Analysis</h3>
        <p style="color: #4b5563; margin-bottom: 1.5rem;">
            Select a candidate from the ranked list to get a detailed breakdown.
        </p>
    """, unsafe_allow_html=True)

    ranked_resumes = st.session_state['ranked_resumes']
    resume_options = {f"{r['filename']} ({r['combined_score']:.1f}%)": r['uuid'] for r in ranked_resumes}

    selected_option = st.selectbox(
        "**Select a Candidate:**",
        options=list(resume_options.keys()),
        index=0
    )

    if st.button("Get Detailed Analysis", use_container_width=True):
        if selected_option:
            selected_uuid = resume_options[selected_option]
            job_id = st.session_state.get('job_id')

            # Use the dedicated endpoint to get detailed analysis
            endpoint = f"/ranker/resume-analysis/{job_id}/{selected_uuid}"

            with st.spinner(f"Fetching detailed analysis for {selected_option}..."):
                # Use a GET request with no data/files
                resp = call_api(endpoint, method="GET")

            if resp and resp.ok:
                analysis = resp.json().get('analysis')
                if analysis:
                    st.subheader("Detailed Breakdown")
                    st.json(analysis)
                else:
                    show_message_box("Could not retrieve detailed analysis for this candidate.", "error")
            elif resp:
                show_message_box(resp.json().get("detail", "Failed to fetch detailed analysis"), "error")

    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="margin-top: 4rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; text-align: center; color: #64748b; font-size: 0.9rem;">
    <div>Resume Ranker AI • Automated Candidate Evaluation System</div>
    <div style="margin-top: 0.5rem;">v1.0.0</div>
</div>

""", unsafe_allow_html=True)