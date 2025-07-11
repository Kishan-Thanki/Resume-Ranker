import csv, io, openpyxl
from io import BytesIO
from openpyxl.utils import get_column_letter

# CSV
def generate_csv_ranked_resumes(ranked_resumes_list: list[dict]) -> bytes:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["uuid", "filename", "score"])
    writer.writeheader()

    for row in ranked_resumes_list:
        writer.writerow(row)

    return output.getvalue().encode("utf-8")

# xlsx
def generate_excel_from_ranked_data(ranked_resumes_list: list[dict]) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Ranked Resumes"

    headers = ["uuid", "filename", "score"]
    ws.append(headers)

    for row in ranked_resumes_list:
        ws.append([row["uuid"], row["filename"], row["score"]])

    for col_num, _ in enumerate(headers, 1):
        column_letter = get_column_letter(col_num)
        ws.column_dimensions[column_letter].auto_size = True

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return output.read()