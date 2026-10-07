import re
from typing import Dict, List, Optional, Tuple

COLUMN_PATTERNS = {
    "date": [
        r"^date$", r"txn\s*date", r"trans(action)?\s*date", r"value\s*date", 
        r"posting\s*date", r"tran\s*date"
    ],
    "description": [
        r"description", r"narration", r"particulars", r"remarks", 
        r"transaction\s*details", r"details", r"transaction\s*remarks"
    ],
    "reference": [
        r"chq(\.|\s|\/)?ref", r"ref(\.|\s|no)?", r"cheque(\s*no)?", 
        r"reference", r"transaction\s*id", r"txn\s*id", r"utr(\s*no)?"
    ],
    "debit": [
        r"withdrawal", r"debit(\s*amount)?", r"^dr(\.|\s*amount)?$", 
        r"debit\s*amt", r"withdraw"
    ],
    "credit": [
        r"deposit", r"credit(\s*amount)?", r"^cr(\.|\s*amount)?$", 
        r"credit\s*amt", r"deposited"
    ],
    "amount": [
        r"^amount$", r"transaction\s*amount", r"txn\s*amount"
    ],
    "type": [
        r"type", r"dr\s*\/?\s*cr", r"transaction\s*type", r"cr\s*\/?\s*dr"
    ],
    "balance": [
        r"balance", r"closing\s*balance", r"available\s*balance", r"net\s*balance"
    ]
}

def detect_column_mapping(columns: List[str]) -> Dict[str, str]:
    """
    Map bank statement columns to standard internal field names:
    date, description, reference, debit, credit, amount, type, balance
    """
    mapping = {}
    normalized_cols = {col: col.strip().lower() for col in columns if col and str(col).strip()}
    
    for standard_name, patterns in COLUMN_PATTERNS.items():
        for original_col, clean_col in normalized_cols.items():
            if standard_name in mapping:
                continue
            for pat in patterns:
                if re.search(pat, clean_col):
                    mapping[standard_name] = original_col
                    break
                    
    return mapping

def detect_bank_from_content(headers: List[str], text_content: str = "") -> str:
    """
    Try to detect the bank name from headers or text content
    """
    content = text_content.upper()
    if "HDFC" in content:
        return "HDFC Bank"
    elif "ICICI" in content:
        return "ICICI Bank"
    elif "STATE BANK" in content or "SBI" in content:
        return "State Bank of India"
    elif "AXIS" in content:
        return "Axis Bank"
    elif "KOTAK" in content:
        return "Kotak Mahindra Bank"
    elif "PUNJAB NATIONAL" in content or "PNB" in content:
        return "Punjab National Bank"
    return "Generic Bank"
