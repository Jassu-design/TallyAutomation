import os
import csv
import openpyxl
from datetime import datetime, timedelta
import random

CSV_DIR = "C:/Users/hp/.gemini/antigravity/scratch/bank-tally-automation/data/sample_bank_statements"
os.makedirs(CSV_DIR, exist_ok=True)

# 1. HDFC Bank Sample CSV
hdfc_csv_path = os.path.join(CSV_DIR, "hdfc_oct_sample.csv")
with open(hdfc_csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["HDFC BANK LIMITED - ACCOUNT STATEMENT"])
    writer.writerow(["Account Number: 50200012345678", "Branch: KORAMANGALA", "Currency: INR"])
    writer.writerow([])
    writer.writerow(["Date", "Narration", "Chq/Ref No", "Value Date", "Withdrawal Amt", "Deposit Amt", "Closing Balance"])
    
    rows = [
        ["01/10/2026", "UPI/AMAZON SELLER SERVICES/428190", "UPI428190331", "01/10/2026", "2350.00", "", "154200.50"],
        ["01/10/2026", "NEFT/ABC INDUSTRIES PVT LTD/SETTLEMENT", "NEFT889102", "01/10/2026", "", "50000.00", "204200.50"],
        ["02/10/2026", "ACH/RELIANCE JIO INFOCOM BILL", "ACH009812", "02/10/2026", "1499.00", "", "202701.50"],
        ["02/10/2026", "HDFC BANK CHARGES Q3 FOLIO", "CHG771829", "02/10/2026", "450.00", "", "202251.50"],
        ["03/10/2026", "UPI/RAJESH KIRANA STORE/987123", "UPI987123001", "03/10/2026", "1850.00", "", "200401.50"],
        ["03/10/2026", "IMPS/SALARY OCTOBER RAJESH/EMP01", "IMPS449102", "03/10/2026", "45000.00", "", "155401.50"],
        ["04/10/2026", "BESCOM ELECTRICITY BILL BANGALORE", "EB9928172", "04/10/2026", "6200.00", "", "149201.50"],
        ["04/10/2026", "INTEREST PAID FOR Q2 FY26", "INT202610", "04/10/2026", "", "3420.00", "152621.50"],
        ["05/10/2026", "SWIGGY BANGALORE ORDERS", "SWIGGY7712", "05/10/2026", "890.00", "", "151731.50"],
        ["05/10/2026", "ATM WDL KORAMANGALA MAIN BR", "ATM881729", "05/10/2026", "10000.00", "", "141731.50"],
        ["06/10/2026", "UPI/UNKNOWN VENDOR HARDWARE", "UPI9921021", "06/10/2026", "3200.00", "", "138531.50"],
        ["06/10/2026", "GOOGLE CLOUD PLATFORM GSUITE", "GCP981203", "06/10/2026", "4200.00", "", "134331.50"],
        ["07/10/2026", "AIRTEL BROADBAND SERVICES BILL", "AIRTEL0012", "07/10/2026", "2199.00", "", "132132.50"],
        ["07/10/2026", "IOCL PETROL PUMP WHITEFIELD", "PETROL991", "07/10/2026", "3000.00", "", "129132.50"],
        ["08/10/2026", "OFFICE RENT OCT 2026 LANDLORD", "RENT88192", "08/10/2026", "35000.00", "", "94132.50"],
    ]
    for r in rows:
        writer.writerow(r)

# 2. ICICI Bank Sample Excel (.xlsx)
icici_xlsx_path = os.path.join(CSV_DIR, "icici_statement_sample.xlsx")
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Statement"

ws.append(["ICICI BANK LTD - DETAILED STATEMENT OF ACCOUNT"])
ws.append(["Customer Name: ABC PVT LTD", "Account: 001105001234"])
ws.append([])
ws.append(["Transaction Date", "Transaction Remarks", "Cheque No", "Debit", "Credit", "Balance"])

icici_rows = [
    ["01-10-2026", "AMAZON PAY INDIA SUPPLIES", "REF00192", 5400.00, None, 580000.00],
    ["01-10-2026", "RTGS CR/ABC INDUSTRIES/ADVANCE PAYMENT", "RTGS88192", None, 125000.00, 705000.00],
    ["02-10-2026", "RELIANCE JIO FIBER RECHARGE", "JIO99182", 2399.00, None, 702601.00],
    ["03-10-2026", "CONSOLIDATED BANK CHARGES GST", "CHG00192", 590.00, None, 702011.00],
    ["04-10-2026", "MONTHLY SALARY DISBURSEMENT STAFF", "SAL202610", 85000.00, None, 617011.00],
    ["05-10-2026", "OFFICE ELECTRICITY BESCOM BILL", "EB009182", 4800.00, None, 612211.00],
    ["06-10-2026", "QUARTERLY FD INTEREST RECEIVED", "INT881920", None, 12450.00, 624661.00],
    ["07-10-2026", "ZOMATO ENTERPRISE SNACKS", "ZOM00192", 1450.00, None, 623211.00],
    ["08-10-2026", "HP PETROL PUMP INDIRANAGAR", "FUEL8819", 2500.00, None, 620711.00],
    ["09-10-2026", "UNIDENTIFIED UPI TRANSFER 9918", "UPI9918", 1200.00, None, 619511.00],
    ["10-10-2026", "CASH DEP BY BRANCH ATM CASH", "CASH8819", None, 25000.00, 644511.00]
]

for r in icici_rows:
    ws.append(r)

wb.save(icici_xlsx_path)
print("Generated sample statements successfully.")
