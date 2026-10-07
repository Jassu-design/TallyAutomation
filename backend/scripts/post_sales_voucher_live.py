import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import httpx
from app.tally.voucher_builder import build_sales_invoice_xml

# Prepare invoice details
xml = build_sales_invoice_xml(
    company_name="Pawan Glasses",
    invoice_no="BKN/3118/26-27",
    date_str="2026-08-02",
    buyer_name="B R Duggar And Company",
    buyer_gstin="08AABCB1234F1Z5",
    sub_total=25574.40,
    cgst_amount=639.36,
    sgst_amount=639.36,
    igst_amount=0.0,
    round_off=-0.12,
    total_amount=26853.00,
    items=[{
        "item_name": "Shree Ram Special Moong Papad (400g Pouch)",
        "hsn": "1905",
        "qty": 120.0,
        "rate": 220.0,
        "discount_percent": 3.125,
        "unit": "Kgs",
        "amount": 25574.40
    }],
    narration="Tax Invoice BKN/3118/26-27 | e-Way Bill: 791657124983 | Veh: RJ-07-GA-4521 | IRN: a29df9c536480b182cb62174c1ee6618588040a4ab8ef4cb97e1f422ebc96f20",
    irn="a29df9c536480b182cb62174c1ee6618588040a4ab8ef4cb97e1f422ebc96f20",
    eway_bill_no="791657124983",
    vehicle_no="RJ-07-GA-4521"
)

print("Sending voucher to TallyPrime (Company: Pawan Glasses)...")
r = httpx.post("http://localhost:9000", content=xml.encode("utf-8"), headers={"Content-Type": "text/xml"}, timeout=10.0)
print("Voucher Post Response:\n", r.text)
