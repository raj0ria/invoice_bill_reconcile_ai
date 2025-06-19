"""
Filename: file_processing.py
Description: Contains functions for handling file uploads and text extraction.
"""
from pathlib import Path
from fastapi import UploadFile, HTTPException
from PyPDF2 import PdfReader
from .logs import logger
from config.config import STORAGE_CLIENT, GCS_BUCKET_NAME

def extract_text_from_pdf_stream(file_stream) -> str:
    """Extracts text directly from an in-memory file stream (like UploadFile)."""
    logger.info("Extracting text from PDF stream.")
    try:
        # Reset stream cursor in case it has been read before
        file_stream.seek(0)
        reader = PdfReader(file_stream)
        return "".join(page.extract_text() for page in reader.pages if page.extract_text())
    except Exception as e:
        logger.error(f"Could not extract text from stream. Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract text from PDF file.")

def upload_file_to_cloud(file: UploadFile) -> str:
    """Uploads a file to GCS and returns its public URL."""
    if not STORAGE_CLIENT or not GCS_BUCKET_NAME:
        raise HTTPException(status_code=500, detail="Google Cloud Storage is not configured.")
    
    try:
        bucket = STORAGE_CLIENT.bucket(GCS_BUCKET_NAME)
        
        # This will cause overwrites.
        blob_name = file.filename

        blob = bucket.blob(blob_name)

        file.file.seek(0)
        
        logger.info(f"Uploading {blob_name} to bucket {GCS_BUCKET_NAME}...")
        blob.upload_from_file(file.file, content_type=file.content_type)
        
        logger.info("Upload successful.")
        return blob.public_url
    except Exception as e:
        logger.error(f"Failed to upload file to GCS. Error: {e}")
        raise HTTPException(status_code=500, detail="Could not upload file to cloud storage.")