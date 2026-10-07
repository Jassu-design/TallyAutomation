import openpyxl
import pandas as pd
from typing import List, Dict, Any, Tuple
from app.ingestion.detector import detect_column_mapping, detect_bank_from_content

def read_excel_statement(file_path: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Reads an Excel (.xlsx or .xls) bank statement, detects header row and columns,
    returns (bank_name, raw_records)
    """
    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet = wb.active
    
    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        raise ValueError("Excel statement sheet is empty.")

    header_idx = -1
    best_mapping = {}
    full_text_list = []

    for i, row in enumerate(rows[:20]):
        row_str_list = [str(cell) if cell is not None else "" for cell in row]
        full_text_list.extend(row_str_list)
        mapping = detect_column_mapping(row_str_list)
        
        has_date = "date" in mapping
        has_desc = "description" in mapping or "reference" in mapping
        has_amt = "amount" in mapping or "debit" in mapping or "credit" in mapping
        
        if has_date and has_desc and has_amt:
            header_idx = i
            best_mapping = mapping
            header_row_values = row_str_list
            break

    if header_idx == -1:
        # Fallback to row 0
        header_idx = 0
        header_row_values = [str(cell) if cell is not None else "" for cell in rows[0]]
        best_mapping = detect_column_mapping(header_row_values)

    bank_name = detect_bank_from_content(list(best_mapping.values()), " ".join(full_text_list))

    # Map column positions by index in header_row_values
    col_index_to_std: Dict[int, str] = {}
    for std_col, orig_header in best_mapping.items():
        for idx, val in enumerate(header_row_values):
            if val.strip() == orig_header.strip():
                col_index_to_std[idx] = std_col
                break

    raw_records: List[Dict[str, Any]] = []
    for row in rows[header_idx + 1:]:
        if not any(row):
            continue
            
        record = {}
        row_str_first = str(row[0] if row[0] is not None else "").strip().lower()
        if "total" in row_str_first or "end of statement" in row_str_first or "opening balance" in row_str_first:
            continue
            
        for idx, cell_val in enumerate(row):
            if idx in col_index_to_std:
                std_col = col_index_to_std[idx]
                record[std_col] = cell_val if cell_val is not None else ""

        # Check if record has valid date or description
        if str(record.get("date", "")).strip() or str(record.get("description", "")).strip():
            raw_records.append(record)

    return bank_name, raw_records
