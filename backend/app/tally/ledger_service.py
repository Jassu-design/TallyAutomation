from typing import List, Dict, Any
from app.tally.client import TallyClient

STANDARD_LEDGERS = [
    {"name": "HDFC Bank Account", "group": "Bank Accounts"},
    {"name": "ICICI Bank Account", "group": "Bank Accounts"},
    {"name": "SBI Bank Account", "group": "Bank Accounts"},
    {"name": "Cash", "group": "Cash-in-hand"},
    {"name": "Amazon Expenses", "group": "Indirect Expenses"},
    {"name": "Telephone Expenses", "group": "Indirect Expenses"},
    {"name": "Salary Expenses", "group": "Indirect Expenses"},
    {"name": "Rent Expenses", "group": "Indirect Expenses"},
    {"name": "Electricity Expenses", "group": "Indirect Expenses"},
    {"name": "Bank Charges", "group": "Indirect Expenses"},
    {"name": "Bank Interest Received", "group": "Indirect Incomes"},
    {"name": "Staff Welfare Expenses", "group": "Indirect Expenses"},
    {"name": "Software & Subscription Expenses", "group": "Indirect Expenses"},
    {"name": "Conveyance Expenses", "group": "Indirect Expenses"},
    {"name": "ABC Industries", "group": "Sundry Debtors"},
    {"name": "Rajesh Kirana Store", "group": "Sundry Creditors"},
    {"name": "Sharma Enterprise", "group": "Sundry Creditors"},
    {"name": "General Sales", "group": "Sales Accounts"},
    {"name": "General Purchase", "group": "Purchase Accounts"},
    {"name": "Suspense Account", "group": "Suspense A/c"},
]

class LedgerService:
    def __init__(self, client: TallyClient = None):
        self.client = client or TallyClient()

    async def get_ledgers(self) -> List[Dict[str, str]]:
        """
        Retrieves list of available ledgers from TallyPrime or defaults.
        """
        # If simulation or fallback
        return STANDARD_LEDGERS
