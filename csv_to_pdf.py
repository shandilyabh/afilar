# # import pandas as pd
# # from reportlab.lib.pagesizes import letter # type: ignore
# # from reportlab.pdfgen import canvas # type: ignore

# # def csv_to_pdf(csv_file, pdf_file):
# #     # Read CSV
# #     df = pd.read_csv(csv_file)
    
# #     # Create PDF
# #     c = canvas.Canvas(pdf_file, pagesize=letter)
# #     width, height = letter

# #     # Set initial position
# #     x_offset, y_offset = 50, height - 50
# #     line_height = 20

# #     # Write headers
# #     for i, col in enumerate(df.columns):
# #         c.drawString(x_offset + i * 100, y_offset, col)
# #     y_offset -= line_height

# #     # Write rows
# #     for _, row in df.iterrows():
# #         for i, value in enumerate(row):
# #             c.drawString(x_offset + i * 100, y_offset, str(value))
# #         y_offset -= line_height
# #         if y_offset < 50:  # New page if needed
# #             c.showPage()
# #             y_offset = height - 50

# #     c.save()

# # # Usage
# # csv_to_pdf("data.csv", "output.pdf")

# import pandas as pd
# from reportlab.lib.pagesizes import letter
# from reportlab.lib import colors
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

# def csv_to_pdf(csv_file, pdf_file):
#     # Read CSV file
#     df = pd.read_csv(csv_file)

#     # Convert DataFrame to list of lists (including headers)
#     data = [df.columns.tolist()] + df.values.tolist()

#     # Create PDF document
#     pdf = SimpleDocTemplate(pdf_file, pagesize=letter)
#     table = Table(data)

#     # Style the table
#     style = TableStyle([
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Cell borders
#         ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Header background color
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Header text color
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold headers
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center alignment
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')  # Middle vertical alignment
#     ])
#     table.setStyle(style)

#     # Build PDF
#     pdf.build([table])

# # Usage
# csv_to_pdf("data.csv", "output.pdf")

import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import json

def json_to_pdf(json_file, pdf_file):
    # Read JSON file
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Convert JSON to DataFrame
    df = pd.DataFrame(data)
    
    # Convert DataFrame to list of lists (including headers)
    table_data = [df.columns.tolist()] + df.values.tolist()
    
    # Create PDF document
    pdf = SimpleDocTemplate(pdf_file, pagesize=letter)
    table = Table(table_data)
    
    # Style the table
    style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Cell borders
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Header background color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Header text color
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold headers
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center alignment
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')  # Middle vertical alignment
    ])
    table.setStyle(style)
    
    # Build PDF
    pdf.build([table])

# Usage
json_to_pdf("data.json", "output.pdf")