# Bank-to-TallyPrime Automation — System Architecture

Version: 1.0  
Status: Production Ready  
Target Environments: Local Accounting Workstation, On-Premises Network, Hybrid

---

## 1. High-Level Architecture Overview

```
 ┌────────────────────────────────────────────────────────┐
 │                   Bank Statements                      │
 │     Excel (.xlsx, .xls) / CSV (.csv)                   │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │                    Ingestion Layer                     │
 │  - Header auto-detection & offset discovery            │
 │  - Multi-bank column mapping (HDFC, ICICI, SBI, Axis)  │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │                   Processing Engine                    │
 │  - Normalization: Dates (ISO), Clean Amounts, Narration│
 │  - Validation: Financial correctness checks            │
 │  - Duplicate Prevention: Deterministic SHA-256 Hash    │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │                    Mapping Engine                      │
 │  - Priority keyword rules & regular expressions        │
 │  - Voucher classification: Payment, Receipt, Contra    │
 │  - Confidence scoring & reason determination           │
 └───────────────────────────┬────────────────────────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   [ Auto-Approved ]                   [ Review Queue ]
   High confidence (≥95%)              Low confidence / Unknown ledger
   Known mapping rules                 User approval / modification
            │                                 │
            └────────────────┬────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │                TallyPrime Integration                  │
 │  - Standard XML Envelope Voucher Generator             │
 │  - Dual Mode: Live Tally HTTP (9000) / Simulation      │
 │  - Response parsing, voucher ID tracking, audit trail  │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │                   Persistence Layer                    │
 │  - SQLite / SQLAlchemy ORM                             │
 │  - Audit Logs, Batches, Transactions, Mappings         │
 └───────────────────────────┬────────────────────────────┘
                             ▲
                             │ REST API (FastAPI)
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │                React + Vite Frontend                   │
 │  - Desktop-first, high contrast accounting interface   │
 │  - Dashboard, Upload, Drawer, Review Queue, Mappings   │
 └────────────────────────────────────────────────────────┘
```

---

## 2. Ingestion & Normalization

1. **Auto Header Discovery**:
   Bank statement files frequently include bank banners or account holder info in the top rows. The engine scans the initial rows, matches column headers against standard patterns, and sets the parsing offset dynamically.
2. **Column Heuristics**:
   - Date: `Date`, `Txn Date`, `Value Date`, `Posting Date`
   - Narration: `Narration`, `Description`, `Particulars`, `Transaction Remarks`
   - Reference: `Chq/Ref No`, `Cheque No`, `Reference`, `Txn ID`
   - Debit: `Withdrawal Amt`, `Debit`, `Dr`
   - Credit: `Deposit Amt`, `Credit`, `Cr`
3. **Normalization**:
   - Dates convert to ISO `YYYY-MM-DD`.
   - Amounts normalize to standard signed 2-decimal floats, stripping currency symbols (`₹`, `$`, commas).
   - Descriptions are trimmed and sanitized of duplicate whitespace.

---

## 3. Duplicate Prevention Mechanism

A unique SHA-256 signature is calculated for each transaction before database insertion:
```
Transaction Hash = SHA-256( BANK_NAME | DATE | AMOUNT | REFERENCE | DESCRIPTION )
```
If this hash already exists in the database or earlier within the batch, the transaction status is immediately flagged as `DUPLICATE`. Duplicates are never auto-posted to TallyPrime and require explicit user override.

---

## 4. Ledger Mapping & Voucher Classification

The mapping engine evaluates configurable rules ordered by descending priority.
- If a rule keyword matches the narration, the designated Tally ledger and voucher type are assigned with 98% confidence.
- Default voucher classification:
  - Bank Debit $\rightarrow$ `Payment`
  - Bank Credit $\rightarrow$ `Receipt`
  - ATM Withdrawal / Cash Deposit $\rightarrow$ `Contra`
  - Bank Charges $\rightarrow$ `Payment` (Ledger: `Bank Charges`)
  - Bank Interest $\rightarrow$ `Receipt` (Ledger: `Bank Interest Received`)
- Transactions with confidence below the threshold (default 95%) or missing ledgers route directly to the **Review Queue**.

---

## 5. TallyPrime XML Integration

TallyPrime accepts voucher transactions via HTTP POST to `http://localhost:9000` containing standard XML payloads:
```xml
<ENVELOPE>
  <HEADER>
    <TALLYREQUEST>Import Data</TALLYREQUEST>
  </HEADER>
  <BODY>
    <IMPORTDATA>
      <REQUESTDESC>
        <REPORTNAME>Vouchers</REPORTNAME>
        <STATICVARIABLES>
          <SVCURRENTCOMPANY>ABC Pvt Ltd</SVCURRENTCOMPANY>
        </STATICVARIABLES>
      </REQUESTDESC>
      <REQUESTDATA>
        <TALLYMESSAGE xmlns:UDF="TallyUDF">
          <VOUCHER VCHTYPE="Payment" ACTION="Create">
            <DATE>20261001</DATE>
            <VOUCHERTYPENAME>Payment</VOUCHERTYPENAME>
            <NARRATION>UPI/AMAZON SELLER SERVICES</NARRATION>
            <ALLLEDGERENTRIES.LIST>
              <LEDGERNAME>Amazon Expenses</LEDGERNAME>
              <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
              <AMOUNT>-2350.00</AMOUNT>
            </ALLLEDGERENTRIES.LIST>
            <ALLLEDGERENTRIES.LIST>
              <LEDGERNAME>HDFC Bank Account</LEDGERNAME>
              <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
              <AMOUNT>2350.00</AMOUNT>
            </ALLLEDGERENTRIES.LIST>
          </VOUCHER>
        </TALLYMESSAGE>
      </REQUESTDATA>
    </IMPORTDATA>
  </BODY>
</ENVELOPE>
```
The integration layer parses the response XML, extracting `<CREATED>1</CREATED>` and `<VOUCHERNUMBER>` or capturing `<LINEERROR>` details. All raw requests and responses are stored in the `tally_postings` audit table.

---

## 6. Simulation Mode Gateway

To allow full local development and end-to-end testing without requiring a running TallyPrime installation on port 9000, the system includes an integrated **Simulation Gateway**.
When active, requests generate authentic simulated voucher responses (`PV-XXXX`, `RV-XXXX`), complete with full XML audit history and status updates. Live Tally communication can be toggled in one click from the UI or `.env`.
