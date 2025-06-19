"""
Filename: file_processing.py
Description: Contains functions for handling file uploads and text extraction.
"""
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException
from PyPDF2 import PdfReader
from .logs import logger

def save_uploaded_file(file: UploadFile, destination_dir: str) -> Path:
    """Saves an uploaded file to a destination and returns its path."""
    try:
        Path(destination_dir).mkdir(parents=True, exist_ok=True)
        file_path = Path(destination_dir) / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File '{file.filename}' saved to '{file_path}'")
        return file_path
    except Exception as e:
        logger.error(f"Failed to save file {file.filename}. Error: {e}")
        raise HTTPException(status_code=500, detail=f"Could not save file: {file.filename}")

def extract_text_from_pdf(file_path: Path) -> str:
    """Extracts text from a PDF file."""
    if not file_path.exists():
        logger.error(f"File not found for text extraction: {file_path}")
        return ""

    logger.info(f"Extracting text from PDF: {file_path}")
    try:
        with open(file_path, 'rb') as pdf_file:
            reader = PdfReader(pdf_file)
            return "".join(page.extract_text() for page in reader.pages if page.extract_text())
    except Exception as e:
        logger.error(f"Could not extract text from {file_path}. Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to extract text from {file_path.name}.")