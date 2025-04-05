"""
this script converts a JSON file to a PDF file using the ReportLab library.
"""

import pandas as pd
from reportlab.lib.pagesizes import letter # type: ignore
from reportlab.lib import colors # type: ignore
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle # type: ignore
import json

def json_to_pdf(json_file, pdf_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    df = pd.DataFrame(data)
    
    table_data = [df.columns.tolist()] + df.values.tolist()
    
    pdf = SimpleDocTemplate(pdf_file, pagesize=letter)
    table = Table(table_data)
    
    style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Cell borders
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Header background color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Header text color
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold headers
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center alignment
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')  # Middle vertical alignment
    ])
    table.setStyle(style)
    
    pdf.build([table])

if __name__ == "__main__":
    json_to_pdf("data.json", "output.pdf")