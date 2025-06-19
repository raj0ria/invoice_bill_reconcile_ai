"""
Filename: ai_processing.py
Description: Handles all interactions with the AI model, including prompts.
"""
import json
from typing import Dict, Any
from fastapi import HTTPException
from config.config import MODEL_INSTANCE
from .logs import logger

INVOICE_PROMPT_TEMPLATE = """
You are a data extraction expert. Extract the following details from the invoice text and return a clean JSON object.
- invoice_number, invoice_date, invoice_due_date, invoice_to, contact_number, email
- invoice_subtotal_due (float), invoice_tax_due (float), invoice_total_due (float)
- line_items: A list of objects, each with 'description', 'hrs_or_quantity', 'rate_or_cost', and 'line_total'.

Text:
{text}

Instructions:
- If a value is not found, use "NA" for strings and 0.0 for numbers.
- Ensure all currency values are returned as numbers (float), not strings.
- The output must be only the JSON object, with no extra text or markdown.
"""

BILL_PROMPT_TEMPLATE = """
You are a data extraction expert. Extract the following details from the bill text and return a clean JSON object.
- bill_number, bill_date, bill_payment_date, bill_paid_by
- bill_subtotal_paid (float), bill_tax_paid (float), bill_total_paid (float)
- line_items: A list of objects, each with 'description' and 'Amount'.

Text:
{text}

Instructions:
- If a value is not found, use "NA" for strings and 0.0 for numbers.
- Ensure all currency values are returned as numbers (float), not strings.
- The output must be only the JSON object, with no extra text or markdown.
"""

def extract_data_with_gemini(text: str, prompt_template: str) -> Dict[str, Any]:
    """Sends text and a prompt to the Gemini API and returns the parsed JSON response."""
    if not MODEL_INSTANCE:
        raise HTTPException(status_code=500, detail="AI Model is not configured. Check API Key.")
    
    prompt = prompt_template.format(text=text)
    try:
        response = MODEL_INSTANCE.generate_content(prompt)
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '').strip()
        return json.loads(cleaned_response)
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON from LLM response: {response.text}")
        raise HTTPException(status_code=500, detail="Failed to parse data from the document.")
    except Exception as e:
        logger.error(f"An error occurred during Gemini API call: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the document.")