from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from .enhanced_similarity import EnhancedSimilarityScorer

def rank_resumes_by_similarity(job_text, resumes):
    """Legacy function for backward compatibility"""
    # Combine all texts
    corpus = [job_text] + [r["text"] for r in resumes]

    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # Compute cosine similarity of each resume with JD (index 0)
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Add scores to resumes
    scored = []
    for i, sim in enumerate(similarities):
        scored.append({
            "filename": resumes[i]["filename"],
            "uuid": resumes[i]["uuid"],
            "score": round(float(sim) * 100, 2)  # percentage
        })

    # Sort descending
    ranked = sorted(scored, key=lambda x: x["score"], reverse=True)
    return ranked

def rank_resumes_enhanced(job_description, resumes):
    """Enhanced ranking with skills-based matching"""
    scorer = EnhancedSimilarityScorer()
    
    # Convert legacy format to enhanced format
    enhanced_resumes = []
    for resume in resumes:
        enhanced_resume = {
            'uuid': resume['uuid'],
            'filename': resume['filename'],
            'raw_text': resume['text'],
            'skills': {},  # Will be populated by enhanced parser
            'experience': {},
            'education': {},
            'contact': {}
        }
        enhanced_resumes.append(enhanced_resume)
    
    # Create job description dict
    job_dict = {'text': job_description}
    
    return scorer.rank_resumes_enhanced(job_dict, enhanced_resumes)
