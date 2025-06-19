"""
Filename: app.py
Description: Entry point of the app, contains API implementation.
"""
import uvicorn
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException

# Import configurations and modular functions
from config.config import UPLOAD_DIRECTORY
from utils.logs import logger
from utils.file_processing import save_uploaded_file, extract_text_from_pdf
from utils.ai_processing import extract_data_with_gemini, INVOICE_PROMPT_TEMPLATE, BILL_PROMPT_TEMPLATE
from utils.reconciliation import perform_reconciliation
from utils.pydantic_models import ReconciliationResponse, InvoiceDetails, BillDetails

app = FastAPI(
    title="AI Invoice Reconciler API",
    description="Upload an invoice and related bills to get a reconciliation summary."
)

@app.get('/', summary="Health Check", tags=["System"])
def health_check():
    """A simple endpoint to confirm the API is running."""
    return {"status": "ok"}

@app.post("/api/invoice/reconcile", response_model=ReconciliationResponse, tags=["Reconciliation"])
async def reconcile_invoice_endpoint(
    invoice_file: UploadFile = File(..., description="The main invoice PDF file."),
    bill_files: List[UploadFile] = File(..., description="A list of bill PDF files.")
):
    """
    Processes an invoice and associated bills, performs AI-powered data extraction,
    and returns a detailed reconciliation report.
    """
    try:
        # --- Process Invoice ---
        logger.info(f"Processing invoice: {invoice_file.filename}")
        invoice_path = save_uploaded_file(invoice_file, UPLOAD_DIRECTORY)
        invoice_text = extract_text_from_pdf(invoice_path)
        invoice_json = extract_data_with_gemini(invoice_text, INVOICE_PROMPT_TEMPLATE)
        invoice_details = InvoiceDetails(**invoice_json)

        # --- Process Bills ---
        bill_details_list = []
        for bill_file in bill_files:
            logger.info(f"Processing bill: {bill_file.filename}")
            bill_path = save_uploaded_file(bill_file, UPLOAD_DIRECTORY)
            bill_text = extract_text_from_pdf(bill_path)
            bill_json = extract_data_with_gemini(bill_text, BILL_PROMPT_TEMPLATE)
            bill_details_list.append(BillDetails(**bill_json))

        # --- Perform Reconciliation ---
        logger.info("Performing reconciliation...")
        reconciliation_data = perform_reconciliation(invoice_details, bill_details_list)
        
        return ReconciliationResponse(
            invoice_details=invoice_details,
            bill_details=bill_details_list,
            result=reconciliation_data
        )
    except HTTPException as e:
        # Forward known HTTP errors
        raise e
    except Exception as e:
        logger.error(f"An unexpected error occurred in the endpoint: {e}", exc_info=True)
        # Catch any other error and return a generic 500
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)