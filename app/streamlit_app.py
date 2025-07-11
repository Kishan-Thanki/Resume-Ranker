import streamlit as st
import requests

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Resume Ranker", layout="centered")
st.title("📄 Resume Ranking App")
st.markdown("Upload a job description and resumes to rank them by relevance.")

# 1. Upload JD
st.header("Step 1: Upload Job Description")
job_text = st.text_area("Or paste job description:")
job_file = st.file_uploader("Or upload a Job file (.txt or .pdf)", type=["txt", "pdf"])

if st.button("Upload JD"):
    if not job_text and not job_file:
        st.warning("Please provide job description text or file.")
    else:
        files = None
        data = {}

        if job_text:
            data["job_text"] = job_text

        if job_file:
            files = {
                "job_file": (job_file.name, job_file, job_file.type or "application/pdf")
            }

        with st.spinner("Uploading JD..."):
            try:
                resp = requests.post(f"{API_BASE}/ranker/upload-job-description/", data=data, files=files)
            except Exception as e:
                st.error(f"Failed to connect: {e}")
                resp = None

        if resp and resp.ok:
            job_id = resp.json()["job_id"]
            st.session_state["job_id"] = job_id
            st.success("✅ Job description uploaded!")
            st.code(job_id, language="text")
        elif resp:
            st.error(resp.json().get("detail", "Upload failed."))

# 2. Upload resumes
st.header("Step 2: Upload Resumes")
resume_files = st.file_uploader("Upload multiple resumes (.pdf)", type="pdf", accept_multiple_files=True)

if st.button("Upload Resumes"):
    job_id = st.session_state.get("job_id")
    if not job_id:
        st.warning("Upload JD first.")
    elif not resume_files:
        st.warning("Please upload at least one resume.")
    else:
        files = [("resumes", (f.name, f, "application/pdf")) for f in resume_files]
        data = {"job_id": job_id}
        with st.spinner("Uploading resumes..."):
            resp = requests.post(f"{API_BASE}/resumes/upload-resume/", data=data, files=files)
        if resp.ok:
            st.success(f"{resp.json()['count']} resumes uploaded.")
        else:
            st.error(resp.json()["detail"])

# 3. Rank resumes
st.header("Step 3: Rank Resumes")

ranked = []

if st.button("Rank Now"):
    job_id = st.session_state.get("job_id")
    if not job_id:
        st.warning("Upload JD and resumes first.")
    else:
        with st.spinner("Ranking..."):
            resp = requests.post(f"{API_BASE}/ranker/rank-resumes/", data={"job_id": job_id})
        if resp.ok:
            result = resp.json()
            ranked = result["ranked_resumes"]
            st.session_state["ranked"] = ranked
            st.success(f"{len(ranked)} resumes ranked.")
            st.dataframe(ranked, use_container_width=True)
        else:
            st.error(resp.json()["detail"])

# 4. Download CSV and Excel buttons
if "ranked" in st.session_state and st.session_state["ranked"]:
    job_id = st.session_state.get("job_id")

    # CSV download
    csv_resp = requests.post(
        f"{API_BASE}/ranker/download-ranked-resumes-csv/",
        data={"job_id": job_id}
    )
    if csv_resp.ok:
        st.download_button(
            label="⬇ Download Ranked CSV",
            data=csv_resp.content,
            file_name="ranked_resumes.csv",
            mime="text/csv"
        )
    else:
        st.error("CSV download failed.")

    # Excel download
    excel_resp = requests.post(
        f"{API_BASE}/ranker/download-ranked-resumes-excel/",
        data={"job_id": job_id}
    )
    if excel_resp.ok:
        st.download_button(
            label="⬇ Download Ranked Excel",
            data=excel_resp.content,
            file_name="ranked_resumes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("Excel download failed.")
