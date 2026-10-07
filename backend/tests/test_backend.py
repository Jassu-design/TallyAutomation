import os
import pytest
from app.ingestion import parse_bank_statement
from app.processing import normalize_transaction, validate_transaction, generate_transaction_hash
from app.mapping import map_transaction, match_rule_to_text, determine_voucher_type, DEFAULT_RULES
from app.database.models import LedgerMapping
from app.tally import build_voucher_xml, TallyClient

def test_normalization():
    raw_debit = {
        "date": "01/10/2026",
        "description": "  UPI/AMAZON PAY   TRANSACTION  ",
        "reference": "12345.0",
        "debit": "₹2,350.50",
        "credit": "",
        "balance": "15,000.00"
    }
    norm = normalize_transaction(raw_debit)
    assert norm["date"] == "2026-10-01"
    assert norm["description"] == "UPI/AMAZON PAY TRANSACTION"
    assert norm["reference"] == "12345"
    assert norm["amount"] == 2350.50
    assert norm["transaction_type"] == "DEBIT"
    assert norm["balance"] == 15000.00

def test_validation():
    valid_rec = {
        "date": "2026-10-01",
        "description": "Sample description",
        "reference": "REF123",
        "amount": 100.0,
        "transaction_type": "DEBIT"
    }
    is_valid, errors = validate_transaction(valid_rec)
    assert is_valid is True
    assert len(errors) == 0

    invalid_rec = {
        "date": "invalid-date",
        "description": "",
        "amount": -50.0,
        "transaction_type": "UNKNOWN"
    }
    is_valid, errors = validate_transaction(invalid_rec)
    assert is_valid is False
    assert len(errors) >= 3

def test_duplicate_hash():
    rec1 = {
        "date": "2026-10-01",
        "description": "UPI/AMAZON",
        "reference": "123",
        "amount": 500.0
    }
    rec2 = {
        "date": "2026-10-01",
        "description": "  upi/amazon  ",
        "reference": "123",
        "amount": 500.00
    }
    hash1 = generate_transaction_hash("HDFC Bank", rec1)
    hash2 = generate_transaction_hash("HDFC Bank", rec2)
    assert hash1 == hash2

def test_mapping_engine():
    rules = [
        LedgerMapping(keyword="AMAZON", ledger_name="Amazon Expenses", voucher_type="Payment", priority=10, active=True),
        LedgerMapping(keyword="ABC INDUSTRIES", ledger_name="ABC Industries", voucher_type="Receipt", priority=10, active=True)
    ]
    ledger, voucher, conf, kw, reason = map_transaction("UPI/AMAZON/ORDER991", "DEBIT", rules)
    assert ledger == "Amazon Expenses"
    assert voucher == "Payment"
    assert conf >= 0.95

    ledger2, voucher2, conf2, kw2, reason2 = map_transaction("NEFT/ABC INDUSTRIES/ADV", "CREDIT", rules)
    assert ledger2 == "ABC Industries"
    assert voucher2 == "Receipt"

    # Unknown
    ledger3, voucher3, conf3, kw3, reason3 = map_transaction("SOME RANDOM STORE", "DEBIT", rules)
    assert ledger3 is None
    assert conf3 < 0.50

def test_tally_voucher_builder():
    xml = build_voucher_xml(
        company_name="ABC Pvt Ltd",
        voucher_type="Payment",
        date_str="2026-10-01",
        amount=2350.00,
        transaction_type="DEBIT",
        bank_ledger="HDFC Bank Account",
        party_ledger="Amazon Expenses",
        narration="UPI Amazon Order",
        reference="REF9910"
    )
    assert "<TALLYREQUEST>Import Data</TALLYREQUEST>" in xml
    assert "<SVCURRENTCOMPANY>ABC Pvt Ltd</SVCURRENTCOMPANY>" in xml
    assert '<VOUCHER VCHTYPE="Payment" ACTION="Create">' in xml
    assert "<DATE>20261001</DATE>" in xml
    assert "<LEDGERNAME>Amazon Expenses</LEDGERNAME>" in xml
    assert "<AMOUNT>-2350.00</AMOUNT>" in xml
    assert "<LEDGERNAME>HDFC Bank Account</LEDGERNAME>" in xml
    assert "<AMOUNT>2350.00</AMOUNT>" in xml

def test_parse_sample_csv():
    csv_file = "C:/Users/hp/.gemini/antigravity/scratch/bank-tally-automation/data/sample_bank_statements/hdfc_oct_sample.csv"
    bank, txns = parse_bank_statement(csv_file)
    assert "HDFC" in bank
    assert len(txns) == 15

def test_parse_sample_excel():
    excel_file = "C:/Users/hp/.gemini/antigravity/scratch/bank-tally-automation/data/sample_bank_statements/icici_statement_sample.xlsx"
    bank, txns = parse_bank_statement(excel_file)
    assert "ICICI" in bank
    assert len(txns) == 11

def test_parse_sample_pdf():
    pdf_file = "C:/Users/hp/.gemini/antigravity/scratch/bank-tally-automation/data/sample_bank_statements/demo_bank_statement.pdf"
    bank, txns = parse_bank_statement(pdf_file)
    assert "HDFC" in bank
    assert len(txns) == 10
    # Check first record extracted properly
    first = txns[0]
    assert first["date"] == "01/10/2026"
    assert "AMAZON" in first["description"]
    assert "2,350.00" in first["debit"]


@pytest.mark.asyncio
async def test_tally_client_simulation():
    client = TallyClient(simulation=True)
    status = await client.test_connection()
    assert status["connected"] is True
    assert status["mode"] == "SIMULATION"

    res = await client.post_voucher("<ENVELOPE></ENVELOPE>", "Payment")
    assert res["success"] is True
    assert res["voucher_number"].startswith("PV-")


def test_parse_shree_ram_papad_tax_invoice():
    from app.ingestion.invoice_parser import is_tax_invoice_pdf, parse_tax_invoice_pdf
    from app.tally import build_sales_invoice_xml
    
    invoice_path = "C:/Users/hp/.gemini/antigravity/scratch/bank-tally-automation/data/sample_bank_statements/shree_ram_papad_invoice.pdf"
    assert os.path.exists(invoice_path)

    seller, txns = parse_bank_statement(invoice_path)
    assert "Shree Ram Papad" in seller
    assert len(txns) == 1
    
    rec = txns[0]
    assert rec["_is_invoice"] is True
    assert rec["_suggested_voucher"] == "Sales"
    assert rec["_suggested_ledger"] == "B R Duggar And Company"
    assert rec["amount"] == 26853.00

    inv = rec["_invoice_data"]
    assert inv["invoice_no"] == "BKN/3118/26-27"
    assert inv["date"] == "2026-08-02"
    assert inv["buyer_gstin"] == "08AABCB1234F1Z5"
    assert inv["sub_total"] == 25574.40
    assert inv["cgst_amount"] == 639.36
    assert inv["sgst_amount"] == 639.36
    assert inv["round_off"] == -0.12
    assert inv["total_amount"] == 26853.00
    assert inv["eway_bill_no"] == "791657124983"
    assert len(inv["items"]) >= 1

    # Verify Sales XML Builder
    xml = build_sales_invoice_xml(
        company_name="Shree Ram Papad Pvt Ltd",
        invoice_no=inv["invoice_no"],
        date_str=inv["date"],
        buyer_name=inv["buyer_name"],
        buyer_gstin=inv["buyer_gstin"],
        sub_total=inv["sub_total"],
        cgst_amount=inv["cgst_amount"],
        sgst_amount=inv["sgst_amount"],
        igst_amount=inv["igst_amount"],
        round_off=inv["round_off"],
        total_amount=inv["total_amount"],
        items=inv["items"],
        irn=inv["irn"],
        eway_bill_no=inv["eway_bill_no"],
        vehicle_no=inv["vehicle_no"]
    )
    assert '<VOUCHER VCHTYPE="Sales" ACTION="Create"' in xml
    assert "<PARTYLEDGERNAME>B R Duggar And Company</PARTYLEDGERNAME>" in xml
    assert "<AMOUNT>-26853.00</AMOUNT>" in xml
    assert "<LEDGERNAME>Sales @ 5%</LEDGERNAME>" in xml
    assert "<AMOUNT>25574.40</AMOUNT>" in xml
    assert "<LEDGERNAME>Output CGST @ 2.5%</LEDGERNAME>" in xml
    assert "<AMOUNT>639.36</AMOUNT>" in xml
    assert "<LEDGERNAME>Output SGST @ 2.5%</LEDGERNAME>" in xml
    assert "<AMOUNT>639.36</AMOUNT>" in xml
    assert "<LEDGERNAME>Round Off</LEDGERNAME>" in xml
    assert "<ALLINVENTORYENTRIES.LIST>" in xml
    assert "Shree Ram Special Moong Papad" in xml

