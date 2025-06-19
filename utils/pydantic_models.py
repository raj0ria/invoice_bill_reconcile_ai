"""
Filename: pydantic_models.py
Description: Defines Pydantic models for data validation and API contracts.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class BillDetails(BaseModel):
    bill_number: str
    bill_date: str
    bill_payment_date: str
    bill_paid_by: str
    bill_subtotal_paid: float
    bill_tax_paid: float
    bill_total_paid: float
    line_items: List[Dict[str, Any]]
    bill_file_url: str

class InvoiceDetails(BaseModel):
    invoice_number: str
    invoice_date: str
    invoice_due_date: str
    invoice_to: str
    contact_number: str
    email: str
    invoice_subtotal_due: float
    invoice_tax_due: float
    invoice_total_due: float
    line_items: List[Dict[str, Any]]
    invoice_file_url: str

class LineItemVerification(BaseModel):
    matched_items: List[Dict[str, Any]]
    mismatched_items: List[Dict[str, Any]]
    discrepancy_found: bool

class ReconciliationResult(BaseModel):
    invoice_number: str
    invoice_subtotal_due: str
    invoice_tax_due: str
    invoice_total_due: str
    bills: List[Dict[str, Any]]
    subtotal_difference: str
    tax_difference: str
    total_difference: str
    discrepancies: bool
    reconciliation_summary: str
    line_item_verification: LineItemVerification

class ReconciliationResponse(BaseModel):
    invoice_details: InvoiceDetails
    bill_details: List[BillDetails]
    result: ReconciliationResult