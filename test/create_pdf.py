"""
Function to create a PDF file from JSON data
records of daily authentication sucesses
and storing it on Firestore.
"""

import pandas as pd
from reportlab.lib.pagesizes import letter # type: ignore
from reportlab.lib import colors # type: ignore
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle # type: ignore
import json
from slack_notification import send_to_slack
import os
import datetime

slack_webhook = os.getenv("SLACK_WEBHOOK_URL")

def store_pdf_on_firestore(pdf_file: str) -> str:
    """
    Function to store the PDF file on Firestore.
    This is a placeholder function and should be implemented according to your Firestore setup.
    """
    # Firestore storage logic here
    # Returns the link to the stored PDF
    return "https://firestore.example.com/path/to/your/pdf"

def json_to_pdf(json_file: list, date: str) -> None:
    """
    Creates a PDF file containing daily
    authentication records

    Args:
        json_file (str): Path to the input JSON file.
        date: to name the file.
    returns:
        None
    """
    # this is supposed to be the read query result from Firestore
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    df = pd.DataFrame(data)
    
    table_data = [df.columns.tolist()] + df.values.tolist()
    
    pdf_file = f"records_{date}.pdf"

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

    pdf_link = store_pdf_on_firestore(pdf_file)
    send_to_slack(
        slack_webhook, 
        datetime.datetime.now(), 
        "pdf", 
        pdf_link
    )

# usage:
if __name__ == "__main__":
    json_to_pdf("data.json", "output.pdf")