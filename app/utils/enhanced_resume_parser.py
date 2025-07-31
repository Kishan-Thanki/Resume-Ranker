import spacy
import re
from typing import Dict, List, Tuple
import fitz
from datetime import datetime

class EnhancedResumeParser:
    def __init__(self):
        # Load English language model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback if spacy model is not installed
            self.nlp = None
        
        # Common skills database
        self.technical_skills = {
            'programming': ['python', 'java', 'javascript', 'js', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'bash', 'shell', 'powershell'],
            'frameworks': ['django', 'flask', 'fastapi', 'react', 'angular', 'vue', 'spring', 'express', 'laravel', 'asp.net', 'node.js', 'jquery', 'bootstrap', 'tailwind', 'material-ui', 'redux', 'vuex', 'next.js', 'nuxt.js'],
            'databases': ['mysql', 'postgresql', 'postgres', 'mongodb', 'redis', 'oracle', 'sqlite', 'sql server', 'mariadb', 'cassandra', 'elasticsearch', 'dynamodb', 'firebase'],
            'cloud': ['aws', 'amazon web services', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s', 'terraform', 'ansible', 'jenkins', 'gitlab ci', 'github actions', 'heroku', 'digitalocean'],
            'tools': ['git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'figma', 'adobe', 'photoshop', 'illustrator', 'sketch', 'postman', 'swagger', 'vscode', 'intellij', 'eclipse', 'vim', 'emacs'],
            'methodologies': ['agile', 'scrum', 'kanban', 'waterfall', 'devops', 'ci/cd', 'tdd', 'bdd', 'lean', 'six sigma'],
            'languages': ['english', 'spanish', 'french', 'german', 'chinese', 'japanese', 'korean', 'hindi', 'arabic', 'portuguese', 'italian', 'russian']
        }
        
        # Experience patterns
        self.experience_patterns = [
            r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?experience',
            r'experience:\s*(\d+)\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:years?|yrs?)\s*in\s*the\s*field',
            r'(\d+)\s*(?:years?|yrs?)\s*professional\s*experience'
        ]
        
        # Education patterns
        self.education_patterns = [
            r'(bachelor|master|phd|doctorate|b\.?s\.?|m\.?s\.?|mba|b\.?a\.?|m\.?a\.?)',
            r'(university|college|institute|school)',
            r'(computer science|cs|information technology|it|software engineering|data science|ai|machine learning)'
        ]
    
    def parse_resume(self, file_path: str) -> Dict:
        """Extract structured data from resume"""
        # Extract text
        text = self.extract_text(file_path)
        
        # Parse different sections
        skills = self.extract_skills(text)
        experience = self.extract_experience(text)
        education = self.extract_education(text)
        contact = self.extract_contact_info(text)
        
        return {
            'raw_text': text,
            'skills': skills,
            'experience': experience,
            'education': education,
            'contact': contact
        }
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
            return ""
        
        return text.strip()
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract technical skills from resume text"""
        found_skills = {}
        text_lower = text.lower()
        
        for category, skill_list in self.technical_skills.items():
            found_skills[category] = []
            for skill in skill_list:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills[category].append(skill)
        
        return found_skills
    
    def extract_experience(self, text: str) -> Dict:
        """Extract work experience information"""
        experience_info = {
            'years_experience': 0,
            'companies': [],
            'positions': []
        }
        
        # Extract years of experience
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                try:
                    experience_info['years_experience'] = max([int(match) for match in matches])
                    break
                except ValueError:
                    continue
        
        # Extract company names (basic pattern)
        company_patterns = [
            r'(?:at|with|for)\s+([A-Z][A-Za-z\s&.,]+(?:Inc|Corp|LLC|Ltd|Company|Co))',
            r'(?:worked\s+at|employed\s+at)\s+([A-Z][A-Za-z\s&.,]+)',
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, text)
            experience_info['companies'].extend([match.strip() for match in matches])
        
        # Extract job titles
        title_patterns = [
            r'(?:as\s+)?([A-Z][A-Za-z\s]+(?:Engineer|Developer|Manager|Analyst|Consultant|Specialist|Lead|Architect))',
            r'(?:position|role|title):\s*([A-Z][A-Za-z\s]+)',
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, text)
            experience_info['positions'].extend([match.strip() for match in matches])
        
        return experience_info
    
    def extract_education(self, text: str) -> Dict:
        """Extract education details"""
        education_info = {
            'degrees': [],
            'institutions': [],
            'fields_of_study': []
        }
        
        # Extract degrees
        degree_pattern = r'\b(bachelor|master|phd|doctorate|b\.?s\.?|m\.?s\.?|mba|b\.?a\.?|m\.?a\.?)\b'
        degrees = re.findall(degree_pattern, text.lower())
        education_info['degrees'] = list(set(degrees))
        
        # Extract institutions
        institution_patterns = [
            r'(?:from|at)\s+([A-Z][A-Za-z\s&.,]+(?:University|College|Institute|School))',
            r'([A-Z][A-Za-z\s&.,]+(?:University|College|Institute|School))',
        ]
        
        for pattern in institution_patterns:
            matches = re.findall(pattern, text)
            education_info['institutions'].extend([match.strip() for match in matches])
        
        # Extract fields of study
        field_patterns = [
            r'(?:in|of)\s+(computer science|cs|information technology|it|software engineering|data science|ai|machine learning|mathematics|physics|chemistry|biology|business|economics)',
            r'(computer science|cs|information technology|it|software engineering|data science|ai|machine learning)',
        ]
        
        for pattern in field_patterns:
            matches = re.findall(pattern, text.lower())
            education_info['fields_of_study'].extend(matches)
        
        return education_info
    
    def extract_contact_info(self, text: str) -> Dict:
        """Extract contact information"""
        contact_info = {
            'email': '',
            'phone': '',
            'location': ''
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_matches = re.findall(email_pattern, text)
        if email_matches:
            contact_info['email'] = email_matches[0]
        
        # Extract phone number
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b',
            r'\b\+\d{1,3}[-.]?\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        ]
        
        for pattern in phone_patterns:
            phone_matches = re.findall(pattern, text)
            if phone_matches:
                contact_info['phone'] = phone_matches[0]
                break
        
        # Extract location (basic pattern)
        location_patterns = [
            r'(?:from|in|based\s+in)\s+([A-Z][A-Za-z\s,]+(?:City|State|Country|CA|NY|TX|FL|IL|PA|OH|GA|NC|MI|NJ|VA|WA|AZ|MA|TN|IN|MO|MD|CO|MN|WI|LA|AL|SC|KY|OR|OK|CT|IA|MS|AR|KS|UT|NV|NM|NE|ID|WV|NH|ME|MT|RI|DE|SD|ND|AK|VT|WY))',
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            if matches:
                contact_info['location'] = matches[0].strip()
                break
        
        return contact_info
    
    def get_skills_summary(self, skills: Dict[str, List[str]]) -> str:
        """Convert skills dictionary to a summary string"""
        all_skills = []
        for category, skill_list in skills.items():
            all_skills.extend(skill_list)
        return ', '.join(all_skills) if all_skills else "No specific skills detected" 