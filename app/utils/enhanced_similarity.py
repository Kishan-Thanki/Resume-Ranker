from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re
from typing import Dict, List

class EnhancedSimilarityScorer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        
        # Skills database for job description parsing
        self.technical_skills = {
            'programming': ['python', 'java', 'javascript', 'js', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'bash', 'shell', 'powershell'],
            'frameworks': ['django', 'flask', 'fastapi', 'react', 'angular', 'vue', 'spring', 'express', 'laravel', 'asp.net', 'node.js', 'jquery', 'bootstrap', 'tailwind', 'material-ui', 'redux', 'vuex', 'next.js', 'nuxt.js'],
            'databases': ['mysql', 'postgresql', 'postgres', 'mongodb', 'redis', 'oracle', 'sqlite', 'sql server', 'mariadb', 'cassandra', 'elasticsearch', 'dynamodb', 'firebase'],
            'cloud': ['aws', 'amazon web services', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s', 'terraform', 'ansible', 'jenkins', 'gitlab ci', 'github actions', 'heroku', 'digitalocean'],
            'tools': ['git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'figma', 'adobe', 'photoshop', 'illustrator', 'sketch', 'postman', 'swagger', 'vscode', 'intellij', 'eclipse', 'vim', 'emacs'],
            'methodologies': ['agile', 'scrum', 'kanban', 'waterfall', 'devops', 'ci/cd', 'tdd', 'bdd', 'lean', 'six sigma'],
            'languages': ['english', 'spanish', 'french', 'german', 'chinese', 'japanese', 'korean', 'hindi', 'arabic', 'portuguese', 'italian', 'russian']
        }
    
    def extract_skills_from_job_description(self, job_text: str) -> Dict[str, List[str]]:
        """Extract required skills from job description"""
        found_skills = {}
        job_text_lower = job_text.lower()
        
        for category, skill_list in self.technical_skills.items():
            found_skills[category] = []
            for skill in skill_list:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, job_text_lower):
                    found_skills[category].append(skill)
        
        return found_skills
    
    def calculate_skill_match_score(self, job_skills: Dict[str, List[str]], resume_skills: Dict[str, List[str]]) -> float:
        """Calculate skill-specific matching score"""
        if not job_skills or not resume_skills:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        # Define weights for different skill categories
        category_weights = {
            'programming': 0.25,
            'frameworks': 0.20,
            'databases': 0.15,
            'cloud': 0.15,
            'tools': 0.10,
            'methodologies': 0.10,
            'languages': 0.05
        }
        
        for category, job_skill_list in job_skills.items():
            if category in resume_skills and job_skill_list:
                resume_skill_list = resume_skills[category]
                
                # Calculate matches
                matches = len(set(job_skill_list) & set(resume_skill_list))
                total_required = len(job_skill_list)
                
                # Calculate category score
                category_score = matches / total_required if total_required > 0 else 0.0
                
                # Apply weight
                weight = category_weights.get(category, 0.05)
                total_score += category_score * weight
                total_weight += weight
        
        # Normalize score
        final_score = (total_score / total_weight) * 100 if total_weight > 0 else 0.0
        return round(final_score, 2)
    
    def calculate_text_similarity(self, job_text: str, resume_text: str) -> float:
        """Calculate text similarity using TF-IDF and cosine similarity"""
        if not job_text.strip() or not resume_text.strip():
            return 0.0
        
        try:
            # Combine texts for vectorization
            corpus = [job_text, resume_text]
            
            # Create TF-IDF vectors
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return round(float(similarity) * 100, 2)
        except Exception as e:
            print(f"Error calculating text similarity: {e}")
            return 0.0
    
    def calculate_experience_match_score(self, job_text: str, resume_experience: Dict) -> float:
        """Calculate experience matching score"""
        # Extract years of experience requirement from job description
        experience_patterns = [
            r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?experience',
            r'experience:\s*(\d+)\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:years?|yrs?)\s*in\s*the\s*field',
            r'(\d+)\s*(?:years?|yrs?)\s*professional\s*experience',
            r'minimum\s+(\d+)\s*(?:years?|yrs?)',
            r'at\s+least\s+(\d+)\s*(?:years?|yrs?)'
        ]
        
        required_years = 0
        for pattern in experience_patterns:
            matches = re.findall(pattern, job_text.lower())
            if matches:
                try:
                    required_years = max([int(match) for match in matches])
                    break
                except ValueError:
                    continue
        
        if required_years == 0 or 'years_experience' not in resume_experience:
            return 50.0  # Neutral score if no experience info
        
        candidate_years = resume_experience.get('years_experience', 0)
        
        # Calculate experience match score
        if candidate_years >= required_years:
            # Bonus for exceeding requirements
            if candidate_years <= required_years + 2:
                return 100.0
            else:
                # Slight penalty for being overqualified
                return max(80.0, 100.0 - (candidate_years - required_years - 2) * 5)
        else:
            # Penalty for not meeting requirements
            return max(0.0, 100.0 - (required_years - candidate_years) * 20)
    
    def rank_resumes_enhanced(self, job_description: Dict, resumes: List[Dict]) -> List[Dict]:
        """Enhanced ranking with multiple scoring factors"""
        if not resumes:
            return []
        
        # Extract skills from job description
        job_skills = self.extract_skills_from_job_description(job_description.get('text', ''))
        
        results = []
        
        for resume in resumes:
            # Calculate skill match score
            skill_score = self.calculate_skill_match_score(
                job_skills,
                resume.get('skills', {})
            )
            
            # Calculate text similarity score
            text_score = self.calculate_text_similarity(
                job_description.get('text', ''),
                resume.get('raw_text', '')
            )
            
            # Calculate experience match score
            experience_score = self.calculate_experience_match_score(
                job_description.get('text', ''),
                resume.get('experience', {})
            )
            
            # Calculate combined score with weights
            # Skills: 50%, Text: 30%, Experience: 20%
            combined_score = (
                skill_score * 0.5 +
                text_score * 0.3 +
                experience_score * 0.2
            )
            
            # Prepare skills summary for display
            skills_summary = self.get_skills_summary(resume.get('skills', {}))
            
            results.append({
                'uuid': resume['uuid'],
                'filename': resume['filename'],
                'skill_score': skill_score,
                'text_score': text_score,
                'experience_score': round(experience_score, 2),
                'combined_score': round(combined_score, 2),
                'skills_found': skills_summary,
                'experience_years': resume.get('experience', {}).get('years_experience', 0),
                'contact_info': resume.get('contact', {})
            })
        
        # Sort by combined score (descending)
        return sorted(results, key=lambda x: x['combined_score'], reverse=True)
    
    def get_skills_summary(self, skills: Dict[str, List[str]]) -> str:
        """Convert skills dictionary to a readable summary"""
        if not skills:
            return "No specific skills detected"
        
        all_skills = []
        for category, skill_list in skills.items():
            if skill_list:
                all_skills.extend(skill_list)
        
        return ', '.join(all_skills) if all_skills else "No specific skills detected"
    
    def get_detailed_analysis(self, job_description: Dict, resume: Dict) -> Dict:
        """Get detailed analysis of a single resume"""
        job_skills = self.extract_skills_from_job_description(job_description.get('text', ''))
        
        skill_score = self.calculate_skill_match_score(
            job_skills,
            resume.get('skills', {})
        )
        
        text_score = self.calculate_text_similarity(
            job_description.get('text', ''),
            resume.get('raw_text', '')
        )
        
        experience_score = self.calculate_experience_match_score(
            job_description.get('text', ''),
            resume.get('experience', {})
        )
        
        combined_score = (
            skill_score * 0.5 +
            text_score * 0.3 +
            experience_score * 0.2
        )
        
        return {
            'overall_score': round(combined_score, 2),
            'skill_analysis': {
                'score': skill_score,
                'required_skills': job_skills,
                'candidate_skills': resume.get('skills', {}),
                'missing_skills': self.get_missing_skills(job_skills, resume.get('skills', {}))
            },
            'text_analysis': {
                'score': text_score,
                'similarity_percentage': text_score
            },
            'experience_analysis': {
                'score': round(experience_score, 2),
                'candidate_years': resume.get('experience', {}).get('years_experience', 0)
            }
        }
    
    def get_missing_skills(self, job_skills: Dict[str, List[str]], resume_skills: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Identify skills that are required but missing from resume"""
        missing_skills = {}
        
        for category, job_skill_list in job_skills.items():
            if category in resume_skills:
                resume_skill_list = resume_skills[category]
                missing = list(set(job_skill_list) - set(resume_skill_list))
                if missing:
                    missing_skills[category] = missing
            else:
                missing_skills[category] = job_skill_list
        
        return missing_skills 