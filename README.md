Resume Ranker: Recruitment Tool
=============================================

Introduction
------------

The **Resume Ranker** is a sophisticated tool designed to streamline the recruitment process. It automates resume screening by parsing, analyzing, and ranking candidates based on their skills, experience, and text similarity to a specific job description. This project aims to enhance hiring efficiency and objectivity by reducing the manual effort required to evaluate a high volume of resumes.

Features
--------

*   **Intelligent Resume Parsing:** Automatically extracts structured data such as skills, experience, education, and contact information from resumes.
    
*   **Multi-Factor Scoring:** Ranks resumes using a customizable, weighted scoring algorithm:
    
    *   **Skills Match (50%):** Compares the candidate's skills against those required in the job description.
        
    *   **Text Similarity (30%):** Measures the relevance of the resume's content to the job description.
        
    *   **Experience Match (20%):** Evaluates the candidate's professional experience against the job requirements.
        
*   **Intuitive User Interface:** Provides a simple frontend for recruiters to upload resumes and job descriptions.
    
*   **Data Export:** Allows for the export of ranking results and detailed scoring breakdowns into CSV and Excel formats for easy analysis.
    
*   **Scalable & Fast:** Designed to handle a large number of resumes with a performance goal of parsing each resume in under 3 seconds.
    

Tech Stack
----------

*   **Backend:** Python, FastAPI (for the REST API), SQLAlchemy (ORM), SpaCy (NLP)
    
*   **Frontend:** Streamlit
    
*   **Deployment:** Render
    

Getting Started
---------------

To get a feel for the application, you can check out the live demo and the GitHub repository.

*   **Live Demo:** https://resume-ranker.kishanthanki.dev/
    
*   **GitHub Repository:** https://github.com/Kishan-Thanki/Resume-Ranker

Project Structure
-----------------

The project is built with a modular and clean codebase to ensure future improvements and maintainability. It follows a standard API-first architecture, making it easy to integrate with other systems.
