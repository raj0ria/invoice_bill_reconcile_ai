"""
Filename: config.py
Description: This file contains application configuration.
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv
from google.cloud import storage

# Load environment variables from a .env file
load_dotenv()

# --- Gemini Configuration ---
try:
    GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
    genai.configure(api_key=GOOGLE_API_KEY)
except KeyError:
    print("WARNING: GOOGLE_API_KEY environment variable not set.")
    GOOGLE_API_KEY = None

GEMINI_MODEL_NAME = "gemini-1.5-pro-latest"
MODEL_INSTANCE = genai.GenerativeModel(GEMINI_MODEL_NAME) if GOOGLE_API_KEY else None

# --- Google Cloud Storage Configuration ---
# The client will automatically use the credentials from the environment variable we'll set later
try:
    STORAGE_CLIENT = storage.Client()
    GCS_BUCKET_NAME = os.environ['GCS_BUCKET_NAME']
except Exception as e:
    print(f"WARNING: GCS not configured. Error: {e}")
    STORAGE_CLIENT = None
    GCS_BUCKET_NAME = None

# --- Application Configuration ---
# UPLOAD_DIRECTORY is no longer needed as we are not saving locally
# UPLOAD_DIRECTORY = "uploads/"

# --- CORS Settings ---
ALLOW_ORIGINS = ["*"]
ALLOW_CREDENTIALS = True
ALLOW_METHODS = ["POST", "GET"]
ALLOW_HEADERS = ["Authorization", "Content-Type"]