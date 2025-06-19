"""
Filename: config.py
Description: This file contains application configuration.
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# --- Gemini Configuration ---
try:
    GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
    genai.configure(api_key=GOOGLE_API_KEY)
except KeyError:
    # This allows the app to start, but it will fail on API calls.
    print("WARNING: GOOGLE_API_KEY environment variable not set.")
    GOOGLE_API_KEY = None

GEMINI_MODEL_NAME = "gemini-1.5-pro-latest"
MODEL_INSTANCE = genai.GenerativeModel(GEMINI_MODEL_NAME) if GOOGLE_API_KEY else None

# --- Application Configuration ---
UPLOAD_DIRECTORY = "uploads/"

# --- CORS Settings ---
ALLOW_ORIGINS = ["*"]
ALLOW_CREDENTIALS = True
ALLOW_METHODS = ["POST", "GET"]
ALLOW_HEADERS = ["Authorization", "Content-Type"]