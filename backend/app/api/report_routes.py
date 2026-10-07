import io
import csv
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db, Transaction, ImportBatch

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/summary")
def get_reports_summary(db: Session = Depends(get_db)):
    # Group by status
    status_counts = db.query(Transaction.status, func.count(Transaction.id)).group_by(Transaction.status).all()
    # Group by voucher type
    voucher_counts = db.query(Transaction.voucher_type, func.count(Transaction.id)).filter(Transaction.voucher_type.isnot(None)).group_by(Transaction.voucher_type).all()
    # Group by bank
    bank_counts = db.query(ImportBatch.bank_name, func.count(ImportBatch.id)).group_by(ImportBatch.bank_name).all()

    # Total amounts
    total_debit = db.query(func.sum(Transaction.amount)).filter(Transaction.transaction_type == "DEBIT").scalar() or 0.0
    total_credit = db.query(func.sum(Transaction.amount)).filter(Transaction.transaction_type == "CREDIT").scalar() or 0.0

    return {
        "status_distribution": {k: v for k, v in status_counts},
        "voucher_distribution": {k: v for k, v in voucher_counts},
        "bank_distribution": {k: v for k, v in bank_counts},
        "financial_summary": {
            "total_debit": round(total_debit, 2),
            "total_credit": round(total_credit, 2),
            "net_flow": round(total_credit - total_debit, 2)
        }
    }

@router.get("/export")
def export_transactions_csv(db: Session = Depends(get_db)):
    txns = db.query(Transaction).order_by(Transaction.date.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        "ID", "Date", "Description", "Reference", "Amount", "Type",
        "Ledger", "Voucher Type", "Status", "Tally Voucher No", "Created At"
    ])
    
    for t in txns:
        writer.writerow([
            t.id, t.date, t.description, t.reference or "", t.amount,
            t.transaction_type, t.ledger or "", t.voucher_type or "",
            t.status, t.tally_voucher_number or "",
            t.created_at.strftime("%Y-%m-%d %H:%M:%S") if t.created_at else ""
        ])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions_export.csv"}
    )
