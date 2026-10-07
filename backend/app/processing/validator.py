import re
from typing import Dict, Any, List, Tuple

def validate_transaction(record: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates normalized transaction against financial rules.
    Returns (is_valid, list_of_error_reasons).
    """
    errors = []

    # Validate date
    date_val = record.get("date")
    if not date_val:
        errors.append("Transaction date is missing or empty.")
    elif not re.match(r"^\d{4}-\d{2}-\d{2}$", str(date_val)):
        errors.append(f"Invalid date format '{date_val}', expected YYYY-MM-DD.")

    # Validate amount
    amount_val = record.get("amount")
    if amount_val is None:
        errors.append("Transaction amount is missing.")
    elif not isinstance(amount_val, (int, float)):
        errors.append(f"Transaction amount must be numeric, got {type(amount_val)}.")
    elif amount_val <= 0:
        errors.append("Transaction amount must be strictly greater than 0.")

    # Validate transaction type
    txn_type = record.get("transaction_type")
    if txn_type not in ["DEBIT", "CREDIT"]:
        errors.append(f"Invalid transaction type '{txn_type}'. Must be DEBIT or CREDIT.")

    # Validate description
    desc = record.get("description")
    if not desc or not str(desc).strip():
        errors.append("Transaction description / narration is missing.")

    is_valid = len(errors) == 0
    return is_valid, errors
