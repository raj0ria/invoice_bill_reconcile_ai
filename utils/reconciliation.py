"""
Filename: reconciliation.py
Description: Core business logic for financial and line-item reconciliation.
"""
from typing import List, Dict, Any, Tuple
from decimal import Decimal, ROUND_HALF_UP

from .pydantic_models import InvoiceDetails, BillDetails


def clean_currency(value: Any) -> Decimal:
    """Removes currency symbols and commas, converts to a Decimal type for precision."""
    if value is None:
        return Decimal('0.00')
    # Use string representation to avoid float inaccuracies during conversion
    return Decimal(str(value).replace('$', '').replace(',', ''))


def match_line_items(invoice_items: List[Dict], bill_items_flat: List[Dict]) -> Tuple[List, List]:
    """Compares line items and returns a tuple of (matched_items, mismatched_items)."""
    mismatches = []
    matched_items = []

    # Use a dictionary of Decimal amounts for precise lookups
    invoice_lookup = {
        item.get('description', '').strip().lower(): clean_currency(item.get('line_total', 0))
        for item in invoice_items
    }

    for b_item in bill_items_flat:
        b_desc = b_item.get('description', '').strip().lower()
        b_amount = clean_currency(b_item.get('Amount') or b_item.get('amount', 0))

        if not b_desc:
            continue

        if b_desc in invoice_lookup:
            i_amount = invoice_lookup[b_desc]
            # Use Decimal comparison for accuracy
            if abs(b_amount - i_amount) < Decimal('0.01'):
                matched_items.append({"description": b_desc.title(), "amount": f"${b_amount:,.2f}", "match": True})
            else:
                mismatches.append({
                    "description": b_desc.title(),
                    "bill_amount": f"${b_amount:,.2f}",
                    "invoice_amount": f"${i_amount:,.2f}",
                    "match": False,
                    "reason": "Amount mismatch"
                })
            del invoice_lookup[b_desc]
        else:
            mismatches.append({
                "description": b_desc.title(),
                "bill_amount": f"${b_amount:,.2f}",
                "invoice_amount": "NA",
                "match": False,
                "reason": "Line item not found in any bill"
            })

    for i_desc, i_amount in invoice_lookup.items():
        mismatches.append({
            "description": i_desc.title(), "bill_amount": "NA", "invoice_amount": f"${i_amount:,.2f}",
            "match": False, "reason": "Line item not found in any bill"
        })

    return matched_items, mismatches


def perform_reconciliation(invoice: InvoiceDetails, bills: List[BillDetails]) -> Dict[str, Any]:
    """
    Aggregates bill totals, calculates differences with precision, and generates
    a mathematically consistent reconciliation summary.
    """
    # Convert all source numbers to Decimal for precision
    invoice_subtotal = Decimal(str(invoice.invoice_subtotal_due))
    invoice_tax = Decimal(str(invoice.invoice_tax_due))

    total_bills_subtotal = sum(Decimal(str(b.bill_subtotal_paid)) for b in bills)
    total_bills_tax = sum(Decimal(str(b.bill_tax_paid)) for b in bills)

    # 1. Calculate sub-differences with full precision
    subtotal_diff = invoice_subtotal - total_bills_subtotal
    tax_diff = invoice_tax - total_bills_tax

    # 2. Derive total_difference from the sum of the other two for consistency
    total_diff = subtotal_diff + tax_diff

    # 3. Create a standard quantizer for rounding to 2 decimal places
    quantizer = Decimal('0.01')
    total_diff_rounded = total_diff.quantize(quantizer, rounding=ROUND_HALF_UP)

    # 4. Determine final summary based on the precise total difference
    discrepancies_exist = abs(total_diff) > Decimal('0.00')

    if not discrepancies_exist:
        summary = "All amounts match perfectly. No discrepancies found."
    else:
        # Use the pre-rounded, consistent variable for the summary message
        summary = f"Discrepancies found. Total amount differs by ${total_diff_rounded:,.2f}."

    # Perform line-item matching
    all_bill_items = [item for bill in bills for item in bill.line_items]
    matched, mismatched = match_line_items(invoice.line_items, all_bill_items)

    # 5. Build the final response dictionary with consistent rounding on all diffs
    return {
        "invoice_number": invoice.invoice_number,
        "invoice_subtotal_due": f"${invoice.invoice_subtotal_due:,.2f}",
        "invoice_tax_due": f"${invoice.invoice_tax_due:,.2f}",
        "invoice_total_due": f"${invoice.invoice_total_due:,.2f}",
        "bills": [b.dict() for b in bills],
        "subtotal_difference": f"${subtotal_diff.quantize(quantizer, rounding=ROUND_HALF_UP):,.2f}",
        "tax_difference": f"${tax_diff.quantize(quantizer, rounding=ROUND_HALF_UP):,.2f}",
        "total_difference": f"${total_diff_rounded:,.2f}",
        "discrepancies": discrepancies_exist,
        "reconciliation_summary": summary,
        "line_item_verification": {
            "matched_items": matched,
            "mismatched_items": mismatched,
            "discrepancy_found": bool(mismatched)
        }
    }