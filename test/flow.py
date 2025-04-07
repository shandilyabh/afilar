"""
ideation of functions 
for afilar
"""

import firebase_admin # type: ignore
from firebase_admin import credentials, firestore, storage # type: ignore
from io import BytesIO # type: ignore
import pandas as pd # type: ignore
from reportlab.lib.pagesizes import letter # type: ignore
from reportlab.lib import colors # type: ignore
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle # type: ignore
import json # type: ignore
from datetime import datetime # type: ignore
import smtplib
from email.mime.text import MIMEText
import numpy as np
import faiss # type: ignore
from email.mime.multipart import MIMEMultipart
import bcrypt # type: ignore

# Initializing Firebase
cred = credentials.Certificate("path/to/your-firebase-adminsdk.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'your-project-id.appspot.com'
})
db = firestore.client()

def authenticate_user():
    """
    Authenticate user
    """
    pass

def retrieve_face_id(faiss_id: int) -> np.ndarray:
    """
    Retrieve facenet embeddings from the
    faiss index based on the faiss ID
    """
    index = faiss.read_index("facialEmbeddings.index")
    embedding = index.reconstruct(faiss_id)
    return embedding

def authenticate_password(username: str, pwd_attempt: str):
    user_doc = {
        "hashed_password": "$2b$12$e0Q1v5Z3x4z5J6Y8f7g9Oe1a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5"  # Example hash
    } # to be replaced by a query to the database to get the hashed password.
    stored_hash = user_doc["hashed_password"].encode('utf-8')
    if bcrypt.checkpw(pwd_attempt.encode('utf-8'), stored_hash):
        return True
    else:
        return False

def create_pdf(logs: dict) -> str:
    """
    Creates a PDF from logs and uploads it to Firebase Storage.
    :param logs: Dictionary containing log data.
    :return: Public URL of the uploaded PDF.
    """
    headers = list(logs.keys())
    values = list(logs.values())

    table_data = [headers]
    for i in range(len(values[0])):
        row = [values[j][i] for j in range(len(values))]
        table_data.append(row)

    pdf_buffer = BytesIO()
    pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    table = Table(table_data)

    style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ])
    table.setStyle(style)

    pdf.build([table])
    pdf_buffer.seek(0)

    pdf_filename = "logs/report.pdf"
    bucket = storage.bucket()
    blob = bucket.blob(pdf_filename)
    blob.upload_from_file(pdf_buffer, content_type='application/pdf')
    blob.make_public()

    pdf_url = blob.public_url
    return pdf_url

def register_new_user(email: str, password: str):
    """
    Registers a new user.
    :param email: User's email address.
    :param
    password: User's password.
    """
    pass

def store_instance_in_db(instance: dict, db_name: str):
    """
    Stores an instance in Firestore database.
    :param instance: The data to store (must be a dictionary).
    :param db_name: The Firestore collection name.
    """
    if not isinstance(instance, dict):
        raise ValueError("Instance must be a dictionary.")

    try:
        doc_ref = db.collection(db_name).add(instance)
        print(f"Stored instance in '{db_name}' with ID: {doc_ref[1].id}")
    except Exception as e:
        print(f"Error storing instance: {e}")

def prepare_faiss_index():
    """
    Prepares the faiss index.
    takes the admin's credentials.
    """
    pass

def verify_liveness():
    """
    Verify liveness
    """
    pass