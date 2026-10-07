import re
from datetime import datetime, date
from typing import Dict, Any, Optional, Tuple

MONTH_MAP = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04",
    "may": "05", "jun": "06", "jul": "07", "aug": "08",
    "sep": "09", "oct": "10", "nov": "11", "dec": "12"
}

def clean_amount_value(val: Any) -> Optional[float]:
    """Converts string/numeric currency values to float."""
    if val is None or val == "":
        return None
    if isinstance(val, (int, float)):
        return float(val)
        
    s = str(val).strip().replace(",", "").replace("₹", "").replace("$", "").replace("Rs.", "").replace("Rs", "").strip()
    # Check for trailing Dr/Cr
    s = re.sub(r"[A-Za-z]+", "", s).strip()
    if not s:
        return None
    try:
        return abs(float(s))
    except ValueError:
        return None

def normalize_date(val: Any) -> Optional[str]:
    """Normalizes date input into YYYY-MM-DD string."""
    if val is None or val == "":
        return None
    if isinstance(val, (datetime, date)):
        return val.strftime("%Y-%m-%d")

    s = str(val).strip()
    # If Excel serialized timestamp or string like '2026-10-01 00:00:00'
    if " " in s:
        s = s.split(" ")[0].strip()

    # Try standard patterns
    patterns = [
        "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d",
        "%d/%m/%y", "%d-%m-%y", "%d %b %Y", "%d-%b-%Y",
        "%d %B %Y", "%d-%B-%Y"
    ]
    for pat in patterns:
        try:
            dt = datetime.strptime(s, pat)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Regex heuristic for DD-Mon-YYYY or DD/MM/YYYY
    match = re.search(r"(\d{1,2})[\/\-\.]([A-Za-z]{3}|\d{1,2})[\/\-\.](\d{2,4})", s)
    if match:
        day, month, year = match.groups()
        if len(year) == 2:
            year = "20" + year
        if month.isalpha():
            month = MONTH_MAP.get(month.lower()[:3], "01")
        return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"

    return s

def clean_description(val: Any) -> str:
    if val is None:
        return ""
    s = str(val).strip()
    # Remove multiple spaces and newlines
    s = re.sub(r"\s+", " ", s)
    return s

def clean_reference(val: Any) -> str:
    if val is None:
        return ""
    s = str(val).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s

def normalize_transaction(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes raw extracted dictionary and produces a standardized transaction record:
    {
        'date': 'YYYY-MM-DD',
        'description': '...',
        'reference': '...',
        'amount': 0.0,
        'transaction_type': 'DEBIT' | 'CREDIT',
        'balance': 0.0 or None
    }
    """
    date_val = normalize_date(raw_data.get("date"))
    description = clean_description(raw_data.get("description"))
    reference = clean_reference(raw_data.get("reference"))
    balance = clean_amount_value(raw_data.get("balance"))

    debit_val = clean_amount_value(raw_data.get("debit"))
    credit_val = clean_amount_value(raw_data.get("credit"))
    amt_val = clean_amount_value(raw_data.get("amount"))
    type_val = str(raw_data.get("type", "")).strip().upper()

    amount = 0.0
    transaction_type = "DEBIT"

    if debit_val is not None and debit_val > 0:
        amount = debit_val
        transaction_type = "DEBIT"
    elif credit_val is not None and credit_val > 0:
        amount = credit_val
        transaction_type = "CREDIT"
    elif amt_val is not None and amt_val > 0:
        amount = amt_val
        if "CR" in type_val or "CREDIT" in type_val or "DEP" in type_val:
            transaction_type = "CREDIT"
        else:
            transaction_type = "DEBIT"
    elif amt_val is not None and amt_val < 0:
        amount = abs(amt_val)
        transaction_type = "DEBIT"

    return {
        "date": date_val,
        "description": description,
        "reference": reference,
        "amount": round(amount, 2),
        "transaction_type": transaction_type,
        "balance": round(balance, 2) if balance is not None else None
    }
