import os
import re
from typing import List, Dict, Any, Tuple
import pdfplumber
from app.ingestion.detector import detect_column_mapping, detect_bank_from_content

def read_pdf_statement(file_path: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Reads a bank statement PDF using pdfplumber, extracts tabular transactions,
    detects bank and column mapping, and returns (bank_name, raw_records).
    """
    raw_records: List[Dict[str, Any]] = []
    full_text = ""
    best_mapping = {}
    col_index_to_std: Dict[int, str] = {}
    detected_bank = "Generic Bank"

    with pdfplumber.open(file_path) as pdf:
        if not pdf.pages:
            raise ValueError("PDF statement is empty (no pages found).")

        # 1. Inspect first page for bank name or tax invoice discovery
        first_page_text = pdf.pages[0].extract_text() or ""
        full_text += first_page_text

        from app.ingestion.invoice_parser import is_tax_invoice_pdf, parse_tax_invoice_pdf
        if is_tax_invoice_pdf(first_page_text):
            inv = parse_tax_invoice_pdf(file_path)
            item_summary = f"{inv['items'][0]['item_name'][:30]}..." if inv.get('items') else 'Goods'
            invoice_record = {
                "date": inv["date"],
                "description": f"Tax Invoice {inv['invoice_no']} to {inv['buyer_name']} ({item_summary})",
                "reference": inv["invoice_no"],
                "amount": inv["total_amount"],
                "debit": str(inv["total_amount"]),
                "credit": "",
                "type": "DEBIT",
                "balance": "",
                "_is_invoice": True,
                "_invoice_data": inv,
                "_suggested_ledger": inv["buyer_name"],
                "_suggested_voucher": "Sales"
            }
            return inv["seller_name"], [invoice_record]

        # 2. Iterate through all pages and extract tables for Bank Statement
        header_found = False


        for page_idx, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            page_text = page.extract_text() or ""
            if page_idx > 0:
                full_text += " " + page_text

            for table in tables:
                if not table:
                    continue

                for row in table:
                    clean_row = [str(cell).strip() if cell is not None else "" for cell in row]
                    if not any(clean_row):
                        continue

                    # If header hasn't been established yet, check if this row is the header
                    if not header_found:
                        mapping = detect_column_mapping(clean_row)
                        has_date = "date" in mapping
                        has_desc = "description" in mapping or "reference" in mapping
                        has_amt = "amount" in mapping or "debit" in mapping or "credit" in mapping

                        if has_date and has_desc and has_amt:
                            best_mapping = mapping
                            header_found = True
                            # Map column index to standard field
                            for std_col, orig_header in best_mapping.items():
                                for idx, val in enumerate(clean_row):
                                    if val.strip() == orig_header.strip():
                                        col_index_to_std[idx] = std_col
                                        break
                            continue

                    # If header found, extract row data
                    if header_found and col_index_to_std:
                        record = {}
                        first_val = clean_row[0].lower()
                        if "total" in first_val or "end of statement" in first_val or "opening balance" in first_val:
                            continue

                        for idx, cell_val in enumerate(clean_row):
                            if idx in col_index_to_std:
                                std_col = col_index_to_std[idx]
                                record[std_col] = cell_val

                        # Check if this row looks like a valid transaction row (has date and (desc or amount))
                        if record.get("date") and (record.get("description") or record.get("amount") or record.get("debit") or record.get("credit")):
                            # Don't add repeated header row on multi-page statements
                            if record.get("date").strip().lower() != "date":
                                raw_records.append(record)

    # Detect bank name from headers and text content
    detected_bank = detect_bank_from_content(list(best_mapping.values()), full_text)

    # 3. Fallback: If table extraction didn't catch rows (e.g. text layout without table borders)
    if not raw_records and full_text:
        raw_records = _fallback_text_regex_parse(full_text)

    return detected_bank, raw_records


def _fallback_text_regex_parse(text: str) -> List[Dict[str, Any]]:
    """
    Fallback regex parser for text-based PDF statements without grid lines.
    Looks for line patterns: Date [Description] [Ref] Amount [Balance]
    """
    records = []
    lines = text.split("\n")
    # Date pattern: DD/MM/YYYY or DD-MM-YYYY
    date_regex = re.compile(r"^(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})")
    amt_regex = re.compile(r"(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)")

    for line in lines:
        line_clean = line.strip()
        match_date = date_regex.match(line_clean)
        if match_date:
            date_str = match_date.group(1)
            rest = line_clean[len(date_str):].strip()
            # Find all currency amounts in the line
            amounts = amt_regex.findall(rest)
            if amounts:
                # Last amount is usually Balance, second to last is Txn Amount
                amount_val = amounts[0] if len(amounts) == 1 else amounts[-2]
                balance_val = amounts[-1] if len(amounts) >= 2 else None
                # Description is everything before the amounts
                first_amt_pos = rest.find(amount_val)
                desc = rest[:first_amt_pos].strip() if first_amt_pos != -1 else rest
                
                # Check for CR / DR
                txn_type = "CREDIT" if ("CR" in line_clean.upper() or "DEPOSIT" in line_clean.upper()) else "DEBIT"

                records.append({
                    "date": date_str,
                    "description": desc,
                    "reference": "",
                    "amount": amount_val,
                    "type": txn_type,
                    "balance": balance_val
                })

    return records
