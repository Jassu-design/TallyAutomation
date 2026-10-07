from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db, Transaction, ImportBatch
from app.tally import TallyClient

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    # Counts
    total_txns = db.query(Transaction).count()
    posted_txns = db.query(Transaction).filter(Transaction.status == "POSTED").count()
    review_txns = db.query(Transaction).filter(Transaction.status == "REVIEW_REQUIRED").count()
    failed_txns = db.query(Transaction).filter(Transaction.status == "FAILED").count()
    duplicate_txns = db.query(Transaction).filter(Transaction.status == "DUPLICATE").count()
    approved_txns = db.query(Transaction).filter(Transaction.status == "APPROVED").count()
    pending_txns = db.query(Transaction).filter(Transaction.status == "PENDING").count()

    # Recent Imports (Last 5)
    recent_imports = db.query(ImportBatch).order_by(desc(ImportBatch.uploaded_at)).limit(5).all()

    # Attention Items
    # 1. Unresolved review items
    review_items = db.query(Transaction).filter(Transaction.status == "REVIEW_REQUIRED").order_by(desc(Transaction.id)).limit(5).all()
    # 2. Failed postings
    failed_items = db.query(Transaction).filter(Transaction.status == "FAILED").order_by(desc(Transaction.id)).limit(5).all()
    # 3. Missing ledgers count
    missing_ledger_count = db.query(Transaction).filter(
        Transaction.status == "REVIEW_REQUIRED",
        Transaction.ledger.is_(None)
    ).count()

    # Tally status
    client = TallyClient()
    tally_status = await client.test_connection()

    return {
        "metrics": {
            "total": total_txns,
            "posted": posted_txns,
            "review": review_txns,
            "failed": failed_txns,
            "duplicate": duplicate_txns,
            "approved": approved_txns,
            "pending": pending_txns
        },
        "tally_status": tally_status,
        "recent_imports": [
            {
                "id": b.id,
                "filename": b.filename,
                "bank_name": b.bank_name,
                "date": b.uploaded_at.strftime("%d %b %Y") if b.uploaded_at else "",
                "transactions": b.total_transactions,
                "posted": b.posted_transactions,
                "review": b.review_transactions,
                "failed": b.failed_transactions,
                "status": b.status
            }
            for b in recent_imports
        ],
        "attention": {
            "review_count": review_txns,
            "failed_count": failed_txns,
            "missing_ledger_count": missing_ledger_count,
            "is_tally_connected": tally_status.get("connected", False),
            "review_samples": [
                {
                    "id": t.id,
                    "description": t.description,
                    "amount": t.amount,
                    "suggested_ledger": t.ledger or "Unknown Ledger",
                    "reason": t.review_reason or "Review required"
                }
                for t in review_items
            ],
            "failed_samples": [
                {
                    "id": t.id,
                    "description": t.description,
                    "amount": t.amount,
                    "error": t.error_message or "Unknown failure"
                }
                for t in failed_items
            ]
        }
    }
