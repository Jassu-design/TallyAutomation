import os
from typing import List, Dict, Any, Tuple
from app.ingestion.csv_reader import read_csv_statement
from app.ingestion.excel_reader import read_excel_statement
from app.ingestion.pdf_reader import read_pdf_statement

def parse_bank_statement(file_path: str, selected_bank: str = None) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Parses a CSV, Excel, or PDF file, auto-detects bank (or uses selected_bank),
    and returns (bank_name, raw_records).
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        detected_bank, records = read_csv_statement(file_path)
    elif ext in [".xlsx", ".xls"]:
        detected_bank, records = read_excel_statement(file_path)
    elif ext == ".pdf":
        detected_bank, records = read_pdf_statement(file_path)
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Allowed: .csv, .xlsx, .xls, .pdf")

    final_bank = selected_bank if (selected_bank and selected_bank != "Auto Detect") else detected_bank
    return final_bank, records

