import hashlib
from typing import Dict, Any

def generate_transaction_hash(bank_name: str, record: Dict[str, Any]) -> str:
    """
    Generates deterministic SHA-256 hash for duplicate detection:
    bank_name + date + amount + reference + description
    """
    bank = (bank_name or "GENERIC").strip().upper()
    date_val = str(record.get("date", "")).strip()
    amt_val = f"{float(record.get('amount', 0.0)):.2f}"
    ref_val = str(record.get("reference", "")).strip().upper()
    desc_val = str(record.get("description", "")).strip().upper()

    raw_signature = f"{bank}|{date_val}|{amt_val}|{ref_val}|{desc_val}"
    return hashlib.sha256(raw_signature.encode("utf-8")).hexdigest()
