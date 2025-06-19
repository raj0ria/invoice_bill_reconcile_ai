"""
Filename: logs.py
Description: Logging utility configuration.
"""
import logging

# Configure logging to print logs to console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get a specific logger for the application
logger = logging.getLogger("reconciliation_app")