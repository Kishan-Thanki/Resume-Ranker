import re
import fitz
from typing import Dict, List
from datetime import datetime
import calendar


class ResumeParser:
    def __init__(self):
        self.technical_skills = {
            'programming': ['python', 'java', 'javascript', 'js', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift',
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

        self.experience_patterns = [
            r'(\d+)\s*\+?\s*(?:years?|yrs?)\s*(?:of\s*)?experience',
            r'experience:\s*(\d+)\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:years?|yrs?)\s*in\s*the\s*field',
            r'(\d+)\s*(?:years?|yrs?)\s*professional\s*experience',
            r'minimum\s+(\d+)\s*(?:years?|yrs?)',
            r'at\s+least\s+(\d+)\s*(?:years?|yrs?)'
        ]

        self.education_patterns = {
            'degrees': r'\b(bachelor|master|phd|doctorate|b\.?s\.?|m\.?s\.?|mba|b\.?a\.?|m\.?a\.?)\b',
            'institutions': [
                r'(?:from|at)\s+([A-Z][A-Za-z\s&.,]+(?:University|College|Institute|School))',
                r'([A-Z][A-Za-z\s&.,]+(?:University|College|Institute|School))',
            ],
            'fields_of_study': [
                r'(?:in|of)\s+(computer science|cs|information technology|it|software engineering|data science|ai|machine learning|mathematics|physics|chemistry|biology|business|economics)',
                r'(computer science|cs|information technology|it|software engineering|data science|ai|machine learning)',
                r'(?:in|of)\s+([A-Z][A-Za-z\s]+(?:Engineering|Science|Technology|Management|Arts))'
            ]
        }

        self.company_patterns = [
            r'(?:at|with|for)\s+([A-Z][A-Za-z\s&.,]+(?:Inc|Corp|LLC|Ltd|Company|Co|Inc|Corp|LLC|Ltd|Company|Co|))',
            r'(?:worked\s+at|employed\s+at)\s+([A-Z][A-Za-z\s&.,]+)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        self.title_patterns = [
            r'(?:as\s+)?([A-Z][A-Za-z\s]+(?:Engineer|Developer|Manager|Analyst|Consultant|Specialist|Lead|Architect))',
            r'(?:position|role|title):\s*([A-Z][A-Za-z\s]+)',
            r'([A-Z][A-Za-z\s]+\s+Engineer|Developer|Manager|Analyst)'
        ]

        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        self.phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b',
            r'\b\+\d{1,3}[-.]?\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        ]
        self.location_patterns = [
            r'(?:from|in|based\s+in)\s+([A-Z][A-Za-z\s,]+(?:City|State|Country|CA|NY|TX|FL|IL|PA|OH|GA|NC|MI|NJ|VA|WA|AZ|MA|TN|IN|MO|MD|CO|MN|WI|LA|AL|SC|KY|OR|OK|CT|IA|MS|AR|KS|UT|NV|NM|NE|ID|WV|NH|ME|MT|RI|DE|SD|ND|AK|VT|WY))',
            r'([A-Z][A-Za-z\s,]+(?:city|state|country|CA|NY))',
            r'([A-Z][A-Za-z\s]+,\s*[A-Z]{2})',
            r'([A-Za-z\s]+,\s*[A-Za-z]+)'
        ]

        # New patterns for date ranges
        self.date_patterns = [
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*–\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|Present)',
            r'\d{4}\s*–\s*\d{4}',
            r'\d{4}\s*–\s*Present'
        ]

    def parse_resume(self, file_path: str) -> Dict:
        text = self.extract_text(file_path)
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
        found_skills = {}
        text_lower = text.lower()

        for category, skill_list in self.technical_skills.items():
            found_skills[category] = []
            for skill in skill_list:
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills[category].append(skill)

        return found_skills

    def extract_experience(self, text: str) -> Dict:
        experience_info = {
            'years_experience': 0,
            'companies': [],
            'positions': []
        }

        # First, try to find a numerical experience value
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                try:
                    experience_info['years_experience'] = max([int(match) for match in matches])
                    # If found, we use this and do not proceed to date-based calculation
                    return experience_info
                except ValueError:
                    continue

        # If no numerical value is found, calculate experience from all found date ranges
        total_months = 0
        date_ranges = re.findall(
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*–\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|Present)',
            text
        )

        # This is a simple and flexible check for context
        for dr in date_ranges:
            try:
                start_date_str, end_date_str = dr.split('–')

                # Clean and parse the dates
                start_date = datetime.strptime(start_date_str.strip(),
                                               '%B %Y') if ' ' in start_date_str else datetime.strptime(
                    start_date_str.strip(), '%b %Y')
                end_date = datetime.now() if 'Present' in end_date_str else datetime.strptime(end_date_str.strip(),
                                                                                              '%B %Y') if ' ' in end_date_str else datetime.strptime(
                    end_date_str.strip(), '%b %Y')

                # Calculate the difference in months
                months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                total_months += months
            except ValueError:
                continue

        if total_months > 0:
            experience_info['years_experience'] = round(total_months / 12, 1)

        # Find companies and positions from the entire text, as they are not always strictly within the work experience section
        for pattern in self.company_patterns:
            matches = re.findall(pattern, text)
            experience_info['companies'].extend([match.strip() for match in matches])

        for pattern in self.title_patterns:
            matches = re.findall(pattern, text)
            experience_info['positions'].extend([match.strip() for match in matches])

        return experience_info

    def extract_education(self, text: str) -> Dict:
        education_info = {
            'degrees': [],
            'institutions': [],
            'fields_of_study': []
        }

        # Find degrees using the improved patterns
        degrees = re.findall(self.education_patterns['degrees'], text.lower())
        education_info['degrees'] = list(set(degrees))

        # Find institutions using the improved patterns
        for pattern in self.education_patterns['institutions']:
            matches = re.findall(pattern, text)
            education_info['institutions'].extend([match.strip() for match in matches])

        # Find fields of study using the improved patterns
        for pattern in self.education_patterns['fields_of_study']:
            matches = re.findall(pattern, text.lower())
            education_info['fields_of_study'].extend(matches)

        return education_info

    def extract_contact_info(self, text: str) -> Dict:
        contact_info = {
            'email': '',
            'phone': '',
            'location': ''
        }

        email_matches = re.findall(self.email_pattern, text)

        if email_matches:
            contact_info['email'] = email_matches[0]

        for pattern in self.phone_patterns:
            phone_matches = re.findall(pattern, text)
            if phone_matches:
                contact_info['phone'] = phone_matches[0]
                break

        # Find location using the improved patterns
        for pattern in self.location_patterns:
            matches = re.findall(pattern, text)

            if matches:
                contact_info['location'] = matches[0].strip()
                break

        return contact_info

    def get_skills_summary(self, skills: Dict[str, List[str]]) -> str:
        all_skills = []

        for category, skill_list in skills.items():
            all_skills.extend(skill_list)

        return ', '.join(all_skills) if all_skills else "No specific skills detected"