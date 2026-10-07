import csv
import io
from typing import List, Dict, Any, Tuple
from app.ingestion.detector import detect_column_mapping, detect_bank_from_content

def read_csv_statement(file_path: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Reads a CSV statement, detects bank and header row, returns (bank_name, raw_transactions)
    """
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    if not lines:
        raise ValueError("CSV statement file is empty.")

    full_text = " ".join(lines[:10])
    
    # Locate header line
    header_idx = -1
    best_mapping = {}
    
    for i, line in enumerate(lines[:15]):  # Search up to first 15 lines
        reader = csv.reader([line])
        row = next(reader, [])
        mapping = detect_column_mapping(row)
        # We need at least 'date' and ('description' or 'reference') and ('debit' or 'credit' or 'amount')
        has_date = "date" in mapping
        has_desc = "description" in mapping or "reference" in mapping
        has_amt = "amount" in mapping or "debit" in mapping or "credit" in mapping
        if has_date and has_desc and has_amt:
            header_idx = i
            best_mapping = mapping
            break

    if header_idx == -1:
        # Fallback to line 0 if it has headers
        reader = csv.reader([lines[0]])
        row = next(reader, [])
        best_mapping = detect_column_mapping(row)
        header_idx = 0

    bank_name = detect_bank_from_content(list(best_mapping.values()), full_text)

    # Now read the rows with csv.DictReader starting from header_idx
    csv_data = "\n".join(lines[header_idx:])
    dict_reader = csv.DictReader(io.StringIO(csv_data))
    
    raw_records: List[Dict[str, Any]] = []
    for row in dict_reader:
        # Skip completely empty or summary footer rows (e.g. Total, End of Statement)
        first_val = str(list(row.values())[0] if row.values() else "").strip().lower()
        if "total" in first_val or "end of statement" in first_val or "opening balance" in first_val:
            continue
            
        record = {}
        for std_col, orig_col in best_mapping.items():
            record[std_col] = row.get(orig_col, "")
            
        # Store original row for debugging/audit
        record["_raw"] = row
        
        # Must have at least a date or description to be a valid row
        if record.get("date") or record.get("description"):
            raw_records.append(record)

    return bank_name, raw_records
