import streamlit as st
import requests

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Resume Ranker AI", layout="centered", page_icon="📄")
st.title("📄 Resume Ranker AI")
st.markdown("Upload a Job Description and multiple resumes — get ranked results based on semantic matching.")

# Divider
st.markdown("---")

# === STEP 1: Upload JD ===
st.header("📝 Step 1: Upload Job Description")

col1, col2 = st.columns(2)
with col1:
    job_text = st.text_area("✍️ Paste job description (optional):")

with col2:
    job_file = st.file_uploader("📄 Or upload a JD file (.txt, .pdf)", type=["txt", "pdf"])

if st.button("📤 Upload JD"):
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
                st.error(f"❌ Connection error: {e}")
                resp = None

        if resp and resp.ok:
            job_id = resp.json()["job_id"]
            st.session_state["job_id"] = job_id
            st.success("✅ Job description uploaded!")
            with st.expander("📄 JD ID"):
                st.code(job_id, language="text")
        elif resp:
            st.error(f"❌ {resp.json().get('detail', 'Upload failed.')}")

# Divider
st.markdown("---")

# === STEP 2: Upload Resumes ===
st.header("📂 Step 2: Upload Resumes")
resume_files = st.file_uploader("📄 Upload multiple resumes (.pdf)", type="pdf", accept_multiple_files=True)

if st.button("📤 Upload Resumes"):
    job_id = st.session_state.get("job_id")
    if not job_id:
        st.warning("Please upload a JD first.")
    elif not resume_files:
        st.warning("Please upload at least one resume.")
    else:
        files = [("resumes", (f.name, f, "application/pdf")) for f in resume_files]
        data = {"job_id": job_id}
        with st.spinner("Uploading resumes..."):
            resp = requests.post(f"{API_BASE}/resumes/upload-resume/", data=data, files=files)
        if resp.ok:
            st.success(f"✅ {resp.json()['count']} resumes uploaded.")
        else:
            st.error(f"❌ {resp.json()['detail']}")

# Divider
st.markdown("---")

# === STEP 3: Rank Resumes ===
st.header("🏆 Step 3: Rank Resumes")

if st.button("🚀 Rank Now"):
    job_id = st.session_state.get("job_id")
    if not job_id:
        st.warning("Please upload both JD and resumes first.")
    else:
        with st.spinner("Ranking resumes..."):
            resp = requests.post(f"{API_BASE}/ranker/rank-resumes/", data={"job_id": job_id})
        if resp.ok:
            result = resp.json()
            ranked = result["ranked_resumes"]
            st.success(f"🎉 {len(ranked)} resumes ranked!")
            st.dataframe(ranked, use_container_width=True)

            # ⬇ Download buttons
            with st.expander("⬇ Download Results"):
                col_csv, col_excel = st.columns(2)

                with col_csv:
                    csv_resp = requests.post(f"{API_BASE}/ranker/download-ranked-resumes-csv/", data={"job_id": job_id})
                    if csv_resp.ok:
                        st.download_button(
                            label="📄 Download CSV",
                            data=csv_resp.content,
                            file_name="ranked_resumes.csv",
                            mime="text/csv"
                        )

                with col_excel:
                    excel_resp = requests.post(f"{API_BASE}/ranker/download-ranked-resumes-excel/", data={"job_id": job_id})
                    if excel_resp.ok:
                        st.download_button(
                            label="📊 Download Excel",
                            data=excel_resp.content,
                            file_name="ranked_resumes.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
        else:
            st.error(f"❌ {resp.json()['detail']}")
