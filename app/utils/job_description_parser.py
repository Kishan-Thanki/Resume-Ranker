import docx

# Now docx is a library used for creating, reading and modifying etc. Word documents by using python.

# Define Text extraction function for Job
def extract_text_job_file(file: str) -> str:
    # Check if the passed file extension is .docx
    if file.filename.endswith('.docx'):
        # Create a document object
        doc = docx.Document(file.file_path)
    elif file.filename.endswith('.txt'):
        # If plain text file read and return
        return file.file.read().decode('utf-8')
    else:
        return f"Invalid format. Upload .docx or .txt"