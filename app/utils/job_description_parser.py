import docx
from fastapi import UploadFile

def extract_text_job_file(file: UploadFile) -> str:
    if file.filename.endswith('.docx'):
        doc = docx.Document(file.file)
        full_text = []

        for para in doc.paragraphs:
            full_text.append(para.text)

        return '\n'.join(full_text)
    elif file.filename.endswith('.txt'):
        return file.file.read().decode('utf-8')
    else:
        return "Invalid format. Upload .docx or .txt"