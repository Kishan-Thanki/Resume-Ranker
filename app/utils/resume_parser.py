import fitz
from .enhanced_resume_parser import EnhancedResumeParser

def extract_text_resume(file_path: str) -> str:
    """Legacy function for backward compatibility"""
    text = ""

    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()

    return text.strip()

def extract_enhanced_resume_data(file_path: str) -> dict:
    """Enhanced resume parsing with structured data extraction"""
    parser = EnhancedResumeParser()
    return parser.parse_resume(file_path)
