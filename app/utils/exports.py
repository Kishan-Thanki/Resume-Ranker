from io import BytesIO
import csv, io, openpyxl
from openpyxl.utils import get_column_letter

# CSV
def generate_csv_ranked_resumes(ranked_resumes_list: list[dict]) -> bytes:
    output = io.StringIO()
    # Enhanced fieldnames to include new scoring data
    fieldnames = ["uuid", "filename", "combined_score", "skill_score", "text_score", "experience_score", "skills_found", "experience_years"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for row in ranked_resumes_list:
        # Map the enhanced data to CSV format
        csv_row = {
            "uuid": row.get("uuid", ""),
            "filename": row.get("filename", ""),
            "combined_score": row.get("combined_score", 0),
            "skill_score": row.get("skill_score", 0),
            "text_score": row.get("text_score", 0),
            "experience_score": row.get("experience_score", 0),
            "skills_found": row.get("skills_found", ""),
            "experience_years": row.get("experience_years", 0)
        }
        writer.writerow(csv_row)

    return output.getvalue().encode("utf-8")

# xlsx
def generate_excel_from_ranked_data(ranked_resumes_list: list[dict]) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Ranked Resumes"

    # Enhanced headers to include new scoring data
    headers = ["uuid", "filename", "combined_score", "skill_score", "text_score", "experience_score", "skills_found", "experience_years"]
    ws.append(headers)

    for row in ranked_resumes_list:
        ws.append([
            row.get("uuid", ""),
            row.get("filename", ""),
            row.get("combined_score", 0),
            row.get("skill_score", 0),
            row.get("text_score", 0),
            row.get("experience_score", 0),
            row.get("skills_found", ""),
            row.get("experience_years", 0)
        ])

    for col_num, _ in enumerate(headers, 1):
        column_letter = get_column_letter(col_num)
        ws.column_dimensions[column_letter].auto_size = True

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return output.read()