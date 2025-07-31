import docx

def extract_text_job_file(file: str) -> str:
    if file.filename.endswith('.docx'):
        doc = docx.Document(file.file_path)
    elif file.filename.endswith('.txt'):
        return file.file.read().decode('utf-8')
    else:
        return f"Invalid format. Upload .docx or .txt"