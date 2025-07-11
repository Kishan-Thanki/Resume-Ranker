import fitz

# Now fitz is a Python library used for data extraction, analysis etc. To PDF and other documents.

# Define Text extraction function
def extract_text_resume(file_path: str) -> str:
    """
    This function takes the resume file_path.
    Iterate it page by page.
    Extract text from each page.
    And returns the extracted whole texted.
    :param file_path:
    :return: text
    """
    text = ""

    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()

    return text.strip()
