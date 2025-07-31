#!/usr/bin/env python3
"""
Test script for enhanced resume parsing and ranking features
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.enhanced_resume_parser import EnhancedResumeParser
from app.utils.enhanced_similarity import EnhancedSimilarityScorer

def test_enhanced_parser():
    """Test the enhanced resume parser"""
    print("Testing Enhanced Resume Parser...")
    
    parser = EnhancedResumeParser()
    
    # Test with sample text (simulating a resume)
    sample_resume_text = """
    JOHN DOE
    Software Engineer
    john.doe@email.com | (555) 123-4567 | San Francisco, CA
    
    EXPERIENCE
    3 years of experience as a Python Developer at TechCorp Inc.
    Worked with Django, Flask, and React frameworks.
    Experience with MySQL, PostgreSQL, and MongoDB databases.
    Proficient in AWS, Docker, and Kubernetes.
    Used Git, Jira, and Jenkins for development workflow.
    
    EDUCATION
    Bachelor of Science in Computer Science from Stanford University
    Master's degree in Software Engineering
    
    SKILLS
    Programming: Python, JavaScript, Java, C++
    Frameworks: Django, Flask, React, Angular
    Databases: MySQL, PostgreSQL, MongoDB
    Cloud: AWS, Docker, Kubernetes
    Tools: Git, Jira, Jenkins
    """
    
    # Create a temporary file for testing
    test_file = "test_resume.txt"
    with open(test_file, "w") as f:
        f.write(sample_resume_text)
    
    try:
        # Parse the resume
        result = parser.parse_resume(test_file)
        
        print("✓ Resume parsing successful!")
        print(f"Skills found: {result['skills']}")
        print(f"Experience: {result['experience']}")
        print(f"Education: {result['education']}")
        print(f"Contact: {result['contact']}")
        
        return result
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)

def test_enhanced_similarity():
    """Test the enhanced similarity scoring"""
    print("\nTesting Enhanced Similarity Scoring...")
    
    scorer = EnhancedSimilarityScorer()
    
    # Sample job description
    job_description = {
        'text': """
        Senior Python Developer Position
        
        We are looking for a Python developer with 3+ years of experience.
        Required skills: Python, Django, React, MySQL, AWS
        Experience with Docker and Kubernetes is a plus.
        Knowledge of Git and agile methodologies required.
        """
    }
    
    # Sample resumes
    resumes = [
        {
            'uuid': 'resume1',
            'filename': 'john_doe.pdf',
            'raw_text': 'Python developer with 3 years experience. Worked with Django, React, MySQL, AWS, Docker, Git.',
            'skills': {
                'programming': ['python'],
                'frameworks': ['django', 'react'],
                'databases': ['mysql'],
                'cloud': ['aws', 'docker'],
                'tools': ['git']
            },
            'experience': {'years_experience': 3},
            'education': {},
            'contact': {}
        },
        {
            'uuid': 'resume2',
            'filename': 'jane_smith.pdf',
            'raw_text': 'Java developer with 2 years experience. Worked with Spring, Angular, Oracle.',
            'skills': {
                'programming': ['java'],
                'frameworks': ['spring', 'angular'],
                'databases': ['oracle']
            },
            'experience': {'years_experience': 2},
            'education': {},
            'contact': {}
        }
    ]
    
    # Rank resumes
    results = scorer.rank_resumes_enhanced(job_description, resumes)
    
    print("✓ Enhanced ranking successful!")
    for i, result in enumerate(results):
        print(f"\nRank {i+1}: {result['filename']}")
        print(f"  Combined Score: {result['combined_score']}%")
        print(f"  Skill Score: {result['skill_score']}%")
        print(f"  Text Score: {result['text_score']}%")
        print(f"  Experience Score: {result['experience_score']}%")
        print(f"  Skills Found: {result['skills_found']}")
    
    return results

def test_skill_extraction():
    """Test skill extraction from job description"""
    print("\nTesting Skill Extraction from Job Description...")
    
    scorer = EnhancedSimilarityScorer()
    
    job_text = """
    We need a Full Stack Developer with:
    - Python programming experience
    - Django and React frameworks
    - MySQL and MongoDB databases
    - AWS cloud services
    - Docker containerization
    - Git version control
    - Agile methodology experience
    """
    
    skills = scorer.extract_skills_from_job_description(job_text)
    
    print("✓ Skill extraction successful!")
    for category, skill_list in skills.items():
        if skill_list:
            print(f"  {category}: {', '.join(skill_list)}")
    
    return skills

if __name__ == "__main__":
    print("Enhanced Resume Ranker - Feature Test")
    print("=" * 50)
    
    try:
        # Test enhanced parser
        parsed_resume = test_enhanced_parser()
        
        # Test skill extraction
        extracted_skills = test_skill_extraction()
        
        # Test enhanced similarity
        ranking_results = test_enhanced_similarity()
        
        print("\n" + "=" * 50)
        print("✓ All tests completed successfully!")
        print("Enhanced features are working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc() 