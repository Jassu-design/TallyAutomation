import re
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.database.models import LedgerMapping

DEFAULT_RULES = [
    {"keyword": "AMAZON", "ledger_name": "Amazon Expenses", "voucher_type": "Payment", "priority": 10},
    {"keyword": "JIO", "ledger_name": "Telephone Expenses", "voucher_type": "Payment", "priority": 10},
    {"keyword": "AIRTEL", "ledger_name": "Telephone Expenses", "voucher_type": "Payment", "priority": 10},
    {"keyword": "ABC INDUSTRIES", "ledger_name": "ABC Industries", "voucher_type": "Receipt", "priority": 10},
    {"keyword": "HDFC BANK CHARGE", "ledger_name": "Bank Charges", "voucher_type": "Payment", "priority": 10},
    {"keyword": "BANK CHARGES", "ledger_name": "Bank Charges", "voucher_type": "Payment", "priority": 9},
    {"keyword": "CHG", "ledger_name": "Bank Charges", "voucher_type": "Payment", "priority": 5},
    {"keyword": "SALARY", "ledger_name": "Salary Expenses", "voucher_type": "Payment", "priority": 8},
    {"keyword": "ELECTRICITY", "ledger_name": "Electricity Expenses", "voucher_type": "Payment", "priority": 8},
    {"keyword": "BESCOM", "ledger_name": "Electricity Expenses", "voucher_type": "Payment", "priority": 8},
    {"keyword": "RENT", "ledger_name": "Rent Expenses", "voucher_type": "Payment", "priority": 8},
    {"keyword": "INTEREST", "ledger_name": "Bank Interest Received", "voucher_type": "Receipt", "priority": 8},
    {"keyword": "SWIGGY", "ledger_name": "Staff Welfare Expenses", "voucher_type": "Payment", "priority": 7},
    {"keyword": "ZOMATO", "ledger_name": "Staff Welfare Expenses", "voucher_type": "Payment", "priority": 7},
    {"keyword": "GOOGLE", "ledger_name": "Software & Subscription Expenses", "voucher_type": "Payment", "priority": 7},
    {"keyword": "PETROL", "ledger_name": "Conveyance Expenses", "voucher_type": "Payment", "priority": 7},
    {"keyword": "FUEL", "ledger_name": "Conveyance Expenses", "voucher_type": "Payment", "priority": 7},
    {"keyword": "ATM WDL", "ledger_name": "Cash", "voucher_type": "Contra", "priority": 9},
    {"keyword": "CASH DEP", "ledger_name": "Cash", "voucher_type": "Contra", "priority": 9},
]

def seed_default_mappings(db: Session):
    """Ensure baseline mapping rules exist in the database."""
    for r in DEFAULT_RULES:
        exists = db.query(LedgerMapping).filter(LedgerMapping.keyword == r["keyword"]).first()
        if not exists:
            mapping = LedgerMapping(
                keyword=r["keyword"],
                ledger_name=r["ledger_name"],
                voucher_type=r["voucher_type"],
                priority=r["priority"],
                active=True
            )
            db.add(mapping)
    db.commit()


def match_rule_to_text(keyword: str, text: str) -> bool:
    """Checks if a keyword or regex matches the description text."""
    clean_keyword = keyword.strip()
    clean_text = text.strip()
    
    # Try case-insensitive substring match
    if clean_keyword.upper() in clean_text.upper():
        return True
        
    # If keyword has regex metacharacters, attempt regex search
    try:
        if re.search(clean_keyword, clean_text, re.IGNORECASE):
            return True
    except re.error:
        pass
        
    return False

def determine_voucher_type(txn_type: str, explicit_voucher: Optional[str] = None) -> str:
    if explicit_voucher and explicit_voucher in ["Payment", "Receipt", "Contra", "Journal"]:
        return explicit_voucher
    return "Receipt" if txn_type == "CREDIT" else "Payment"

def map_transaction(
    description: str,
    txn_type: str,
    mappings: List[LedgerMapping]
) -> Tuple[Optional[str], str, float, Optional[str], Optional[str]]:
    """
    Evaluates rules against transaction.
    Returns: (ledger, voucher_type, confidence, matched_keyword, reason)
    """
    desc_upper = (description or "").upper()

    # Iterate through rules sorted by priority descending
    for rule in sorted(mappings, key=lambda x: x.priority, reverse=True):
        if not rule.active:
            continue
        if match_rule_to_text(rule.keyword, desc_upper):
            voucher = determine_voucher_type(txn_type, rule.voucher_type)
            return rule.ledger_name, voucher, 0.98, rule.keyword, None

    # Fallback heuristic rules
    if "INTEREST" in desc_upper and txn_type == "CREDIT":
        return "Bank Interest Received", "Receipt", 0.90, "INTEREST", None
    if "BANK CHARGE" in desc_upper or "CHG" in desc_upper:
        return "Bank Charges", "Payment", 0.90, "BANK CHARGE", None
    if "ATM WDL" in desc_upper or "CASH DEP" in desc_upper:
        return "Cash", "Contra", 0.90, "CASH/ATM", None

    # Default fallback when unknown
    default_voucher = "Receipt" if txn_type == "CREDIT" else "Payment"
    return None, default_voucher, 0.35, None, "Unknown Ledger: No mapping rule matched"
