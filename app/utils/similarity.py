import re
import spacy
from typing import Dict, List
from spacy.matcher import PhraseMatcher

class SimilarityScorer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

        self.technical_skills = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift',
                            'kotlin', 'scala', 'r', 'matlab', 'perl', 'bash', 'shell', 'powershell'],
            'frameworks': ['django', 'flask', 'fastapi', 'react', 'angular', 'vue', 'spring', 'express', 'laravel',
                           'asp.net', 'node.js', 'jquery', 'bootstrap', 'tailwind', 'material-ui', 'redux', 'vuex',
                           'next.js', 'nuxt.js'],
            'databases': ['mysql', 'postgresql', 'postgres', 'mongodb', 'redis', 'oracle', 'sqlite', 'sql server',
                          'mariadb', 'cassandra', 'elasticsearch', 'dynamodb', 'firebase'],
            'cloud': ['aws', 'amazon web services', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s',
                      'terraform', 'ansible', 'jenkins', 'gitlab ci', 'github actions', 'heroku', 'digitalocean'],
            'tools': ['git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'figma', 'adobe', 'photoshop',
                      'illustrator', 'sketch', 'postman', 'swagger', 'vscode', 'intellij', 'eclipse', 'vim', 'emacs'],
            'methodologies': ['agile', 'scrum', 'kanban', 'waterfall', 'devops', 'ci/cd', 'tdd', 'bdd', 'lean',
                              'six sigma'],
            'languages': ['english', 'spanish', 'french', 'german', 'chinese', 'japanese', 'korean', 'hindi', 'arabic',
                          'portuguese', 'italian', 'russian']
        }

    def _find_skills_with_spacy(self, text: str, skill_list: List[str]) -> List[str]:
        # Creates a case-insensitive phrase matcher for finding skills from a predefined list.
        matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")

        # Processes a list of text skills into a format suitable for the PhraseMatcher.
        patterns = []
        for skill in skill_list:
            patterns.append(self.nlp(skill))

        # Adds the prepared skill patterns to the matcher under the label "SKILLS".
        matcher.add("SKILLS", patterns)

        # Processes the raw text into a spaCy Doc object for linguistic analysis.
        doc = self.nlp(text)

        # Runs the PhraseMatcher on the Doc object to find all skill matches.
        matches = matcher(doc)

        found_skills = set()
        for _, start, end in matches:
            # Adds the matched skill text to the set, preventing duplicates.
            found_skills.add(doc[start:end].text)

        return list(found_skills)

    def extract_contact_info(self, text: str) -> Dict[str, str]:
        # Processes the raw text into a spaCy Doc object for linguistic analysis.
        doc = self.nlp(text)
        contact_info = {
            'email': '',
            'phone': '',
            'location': ''
        }

        email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
        phone_pattern = r'(?:\+\d{1,2}\s?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'

        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group(0)

        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group(0)

        # Iterates through the entities identified by spaCy in the document.
        for ent in doc.ents:
            # Checks if the current entity is labeled as a Geopolitical Entity
            if ent.label_ == 'GPE':
                contact_info['location'] = ent.text
                break

        return contact_info

    def extract_skills_from_job_description(self, job_text: str) -> Dict[str, List[str]]:
        found_skills = {}
        for category, skill_list in self.technical_skills.items():
            found_skills[category] = self._find_skills_with_spacy(job_text, skill_list)

        return found_skills

    def preprocess_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^a-z\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def calculate_text_score(self, job_text: str, resume_text: str) -> float:
        job_text_processed = self.preprocess_text(job_text)
        resume_text_processed = self.preprocess_text(resume_text)

        # Processes the raw text into a spaCy Doc object for linguistic analysis.
        job_doc = self.nlp(job_text_processed)
        resume_doc = self.nlp(resume_text_processed)

        # Extracts all unique noun phrases (key topics) from the text.
        job_phrases = set(chunk.text for chunk in job_doc.noun_chunks)
        resume_phrases = set(chunk.text for chunk in resume_doc.noun_chunks)

        # Returns a score of 0.0 if the job_phreases has no phrases to match, preventing a division-by-zero error.
        if not job_phrases:
            return 0.0

        # Counts the number of unique phrases shared by both the job description and the resume.
        matches = len(job_phrases.intersection(resume_phrases))
        # Calculates the percentage of job description phrases that are present in the resume.
        score = (matches / len(job_phrases)) * 100

        return round(score, 2)

    def calculate_skill_match_score(self, job_skills: Dict[str, List[str]], resume_skills: Dict[str, List[str]]) -> float:
        if not job_skills or not resume_skills:
            return 0.0

        total_score = 0.0
        total_weight = 0.0

        category_weights = {
            'programming': 0.25, 'frameworks': 0.20, 'databases': 0.15,
            'cloud': 0.15, 'tools': 0.10, 'methodologies': 0.10, 'languages': 0.05
        }

        for category, job_skill_list in job_skills.items():
            if category in resume_skills and job_skill_list:
                # Gets the candidate's skills list for the current category.
                resume_skill_list = resume_skills[category]

                # Standardizes job skills into a clean, lowercase set for efficient comparison.
                job_skill_set = set(s.lower().strip() for s in job_skill_list)

                # Standardizes resume skills into a clean, lowercase set for comparison.
                resume_skill_set = set(s.lower().strip() for s in resume_skill_list)

                # Counts the number of exactly matching skills between the job and the resume.
                matches = len(job_skill_set & resume_skill_set)

                # Counts the total number of unique skills required by the job in this category.
                total_required = len(job_skill_set)

                # Calculates the match score for the category as a percentage, with a division-by-zero safeguard.
                category_score = matches / total_required if total_required > 0 else 0.0

                # Retrieves the importance weight for the current skill category.
                weight = category_weights.get(category, 0.05)

                # Adds the weighted category score to the running total.
                total_score += category_score * weight

                # Adds the category's weight to a running total for later normalization.
                total_weight += weight

        final_score = (total_score / total_weight) * 100 if total_weight > 0 else 0.0

        return round(final_score, 2)

    def calculate_experience_match_score(self, job_text: str, resume_experience: Dict) -> float:
        experience_patterns = [
            r'experience\s+required:\s*(\d+)\s*\+?\s*years?',
            r'(\d+)\s*\+?\s*(?:years?|yrs?)\s*(?:of\s*)?experience',
            r'experience:\s*(\d+)\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:years?|yrs?)\s*in\s*the\s*field',
            r'(\d+)\s*(?:years?|yrs?)\s*professional\s*experience',
            r'minimum\s+(\d+)\s*(?:years?|yrs?)',
            r'at\s+least\s+(\d+)\s*(?:years?|yrs?)'
        ]

        required_years = 0
        job_text_lower = job_text.lower()

        # Loops through patterns to find the highest number of years required.
        for pattern in experience_patterns:
            matches = re.findall(pattern, job_text_lower)
            # If a match is found, sets the required years and exits the loop.
            if matches:
                try:
                    required_years = max([int(match) for match in matches])
                    break
                except ValueError:
                    continue

        # Returns 100% if no years were specified or if the resume lacks experience data.
        if required_years == 0 or 'years_experience' not in resume_experience:
            return 100.0

        # Gets the candidate's years of experience, defaulting to 0.
        candidate_years = resume_experience.get('years_experience', 0)

        # Checks if the candidate meets or exceeds the required experience.
        if candidate_years >= required_years:
            # Returns 100% for an ideal match (up to 2 years over).
            if candidate_years <= required_years + 2:
                return 100.0
            else:
                # Penalizes overqualified candidates, but keeps score above 80%.
                return max(80.0, 100.0 - (candidate_years - required_years - 2) * 5)
        else:
            # Heavily penalizes underqualified candidates.
            return max(0.0, 100.0 - (required_years - candidate_years) * 20)

    def rank_resumes_enhanced(self, job_description: Dict, resumes: List[Dict]) -> List[Dict]:
        if not resumes:
            return []

        # Extracts and categorizes all required skills from the job description.
        job_skills = self.extract_skills_from_job_description(job_description.get('text', ''))

        # Gets the raw text of the job description for use in other scoring functions.
        job_text = job_description.get('text', '')

        results = []

        for resume in resumes:
            # Calculates a weighted skill match score by comparing the job skills to the candidate's skills.
            skill_score = self.calculate_skill_match_score(job_skills, resume.get('skills', {}))

            # Calculates a score based on how well the candidate's years of experience align with the job's requirements.
            experience_score = self.calculate_experience_match_score(job_text, resume.get('experience', {}))

            # Calculates a text similarity score by comparing the job and resume text using noun phrases.
            text_score = self.calculate_text_score(job_text, resume.get('text', ''))

            combined_score = (skill_score * 0.5 + experience_score * 0.3 + text_score * 0.2)

            skills_summary = self.get_skills_summary(resume.get('skills', {}))
            contact_info = self.extract_contact_info(resume.get('text', ''))

            results.append({
                'uuid': resume['uuid'], 'filename': resume['filename'], 'skill_score': skill_score,
                'text_score': text_score, 'experience_score': round(experience_score, 2),
                'combined_score': round(combined_score, 2), 'skills_found': skills_summary,
                'experience_years': resume.get('experience', {}).get('years_experience', 0),
                'contact_info': contact_info
            })

        # Sorts the list of candidate results by their combined_score in descending order, ranking the resumes from highest to lowest.
        return sorted(results, key=lambda x: x['combined_score'], reverse=True)

    def get_skills_summary(self, skills: Dict[str, List[str]]) -> str:
        if not skills:
            return "No specific skills detected"

        all_skills = [s for skill_list in skills.values() for s in skill_list if skill_list]
        # Joins the skills into a comma-separated string or returns a default message if the list is empty.
        return ', '.join(all_skills) if all_skills else "No specific skills detected"

    def get_detailed_analysis(self, job_description: Dict, resume: Dict) -> Dict:
        job_text = job_description.get('text', '')
        job_skills = self.extract_skills_from_job_description(job_text)

        resume_text = resume.get('text', '')
        contact_info = self.extract_contact_info(resume_text)

        skill_score = self.calculate_skill_match_score(job_skills, resume.get('skills', {}))
        experience_score = self.calculate_experience_match_score(job_text, resume.get('experience', {}))
        text_score = self.calculate_text_score(job_text, resume_text)

        combined_score = (skill_score * 0.5 + experience_score * 0.3 + text_score * 0.2)
        missing_skills_dict = self.get_missing_skills(job_skills, resume.get('skills', {}))

        return {
            'overall_score': round(combined_score, 2),
            'skill_analysis': {
                'score': skill_score, 'required_skills': job_skills, 'candidate_skills': resume.get('skills', {}),
                'missing_skills': missing_skills_dict
            },
            'text_analysis': {
                'score': text_score, 'similarity_percentage': text_score
            },
            'experience_analysis': {
                'score': round(experience_score, 2),
                'candidate_years': resume.get('experience', {}).get('years_experience', 0)
            },
            'contact_info': contact_info
        }

    def get_missing_skills(self, job_skills: Dict[str, List[str]], resume_skills: Dict[str, List[str]]) -> Dict[str, List[str]]:
        missing_skills = {}

        for category, job_skill_list in job_skills.items():
            job_skill_set = set(s.lower().strip() for s in job_skill_list)
            resume_skill_set = set(s.lower().strip() for s in resume_skills.get(category, []))

            missing = list(job_skill_set - resume_skill_set)

            if missing:
                missing_skills[category] = missing

        return missing_skills
