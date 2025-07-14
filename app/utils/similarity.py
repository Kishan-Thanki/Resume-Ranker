from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

def rank_resumes_by_similarity(job_text, resumes):
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
