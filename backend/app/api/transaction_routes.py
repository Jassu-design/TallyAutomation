from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc

from app.database import get_db, Transaction, AuditLog, TallyPosting
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])

class TransactionUpdateRequest(BaseModel):
    ledger: Optional[str] = None
    voucher_type: Optional[str] = None
    date: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None

class ApproveRequest(BaseModel):
    ledger: Optional[str] = None
    voucher_type: Optional[str] = None

class RejectRequest(BaseModel):
    reason: Optional[str] = "Rejected by user"

class BulkApproveRequest(BaseModel):
    transaction_ids: List[int]

@router.get("")
def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=5, le=200),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    transaction_type: Optional[str] = Query(None),
    ledger: Optional[str] = Query(None),
    voucher_type: Optional[str] = Query(None),
    import_id: Optional[int] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    sort_by: str = Query("date"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db)
):
    query = db.query(Transaction)

    if search:
        term = f"%{search}%"
        query = query.filter(or_(
            Transaction.description.ilike(term),
            Transaction.reference.ilike(term),
            Transaction.ledger.ilike(term)
        ))

    if status and status.upper() != "ALL":
        query = query.filter(Transaction.status == status.upper())

    if transaction_type and transaction_type.upper() != "ALL":
        query = query.filter(Transaction.transaction_type == transaction_type.upper())

    if ledger:
        query = query.filter(Transaction.ledger == ledger)

    if voucher_type and voucher_type.upper() != "ALL":
        query = query.filter(Transaction.voucher_type == voucher_type)

    if import_id:
        query = query.filter(Transaction.import_id == import_id)

    if date_from:
        query = query.filter(Transaction.date >= date_from)
    if date_to:
        query = query.filter(Transaction.date <= date_to)

    total = query.count()

    # Sorting
    sort_col = getattr(Transaction, sort_by, Transaction.date)
    query = query.order_by(desc(sort_col) if sort_order.lower() == "desc" else asc(sort_col))

    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 1,
        "items": [
            {
                "id": t.id,
                "import_id": t.import_id,
                "date": t.date,
                "description": t.description,
                "reference": t.reference,
                "amount": t.amount,
                "transaction_type": t.transaction_type,
                "balance": t.balance,
                "ledger": t.ledger,
                "voucher_type": t.voucher_type,
                "status": t.status,
                "confidence": t.confidence,
                "review_reason": t.review_reason,
                "tally_voucher_number": t.tally_voucher_number,
                "tally_response": t.tally_response,
                "error_message": t.error_message,
                "created_at": t.created_at.strftime("%Y-%m-%d %H:%M:%S") if t.created_at else None
            }
            for t in items
        ]
    }

@router.get("/review-queue")
def get_review_queue(
    reason_filter: str = Query("all"),  # all, unknown_ledger, low_confidence, duplicate, other
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Returns items requiring human decision.
    """
    query = db.query(Transaction).filter(
        Transaction.status.in_(["REVIEW_REQUIRED", "DUPLICATE"])
    )

    if reason_filter == "unknown_ledger":
        query = query.filter(Transaction.ledger.is_(None))
    elif reason_filter == "duplicate":
        query = query.filter(Transaction.status == "DUPLICATE")
    elif reason_filter == "low_confidence":
        query = query.filter(Transaction.confidence < 0.90, Transaction.status == "REVIEW_REQUIRED")

    items = query.order_by(desc(Transaction.id)).limit(limit).all()
    total_review = db.query(Transaction).filter(Transaction.status.in_(["REVIEW_REQUIRED", "DUPLICATE"])).count()

    return {
        "total": len(items),
        "total_in_queue": total_review,
        "filter": reason_filter,
        "items": [
            {
                "id": t.id,
                "date": t.date,
                "description": t.description,
                "reference": t.reference,
                "amount": t.amount,
                "transaction_type": t.transaction_type,
                "ledger": t.ledger,
                "voucher_type": t.voucher_type,
                "status": t.status,
                "confidence": t.confidence,
                "review_reason": t.review_reason
            }
            for t in items
        ]
    }

@router.get("/{txn_id}")
def get_transaction_details(txn_id: int, db: Session = Depends(get_db)):
    txn = db.query(Transaction).filter(Transaction.id == txn_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    # Fetch audit timeline
    audits = db.query(AuditLog).filter(
        AuditLog.entity_type == "Transaction",
        AuditLog.entity_id == txn_id
    ).order_by(AuditLog.timestamp.asc()).all()

    # Fetch Tally postings
    postings = db.query(TallyPosting).filter(TallyPosting.transaction_id == txn_id).order_by(TallyPosting.posted_at.desc()).all()

    # Build canonical audit timeline
    timeline = []
    # 1. Imported
    timeline.append({
        "step": "Imported",
        "timestamp": txn.created_at.strftime("%Y-%m-%d %H:%M:%S") if txn.created_at else "",
        "details": f"Imported from {txn.import_batch.filename if txn.import_batch else 'Bank Statement'}"
    })
    # 2. Validated
    timeline.append({
        "step": "Validated",
        "timestamp": txn.created_at.strftime("%Y-%m-%d %H:%M:%S") if txn.created_at else "",
        "details": "Normalized and validated against financial formatting rules"
    })
    # 3. Mapped
    if txn.ledger:
        timeline.append({
            "step": f"Mapped to: {txn.ledger}",
            "timestamp": txn.created_at.strftime("%Y-%m-%d %H:%M:%S") if txn.created_at else "",
            "details": f"Voucher type: {txn.voucher_type} (Confidence: {int(txn.confidence * 100)}%)"
        })
    # 4. Approved
    if txn.status in ["APPROVED", "POSTED", "POSTING"]:
        timeline.append({
            "step": "Approved",
            "timestamp": txn.updated_at.strftime("%Y-%m-%d %H:%M:%S") if txn.updated_at else "",
            "details": "Approved for TallyPrime posting"
        })
    # 5. Posted
    if txn.status == "POSTED":
        timeline.append({
            "step": "Posted to TallyPrime",
            "timestamp": txn.updated_at.strftime("%Y-%m-%d %H:%M:%S") if txn.updated_at else "",
            "details": f"Voucher No: {txn.tally_voucher_number or 'PV-1023'}"
        })
    elif txn.status == "FAILED":
        timeline.append({
            "step": "Posting Failed",
            "timestamp": txn.updated_at.strftime("%Y-%m-%d %H:%M:%S") if txn.updated_at else "",
            "details": txn.error_message or "TallyPrime integration error"
        })

    return {
        "id": txn.id,
        "import_id": txn.import_id,
        "import_file": txn.import_batch.filename if txn.import_batch else None,
        "bank_name": txn.import_batch.bank_name if txn.import_batch else "Auto Detect",
        "transaction_hash": txn.transaction_hash,
        "date": txn.date,
        "description": txn.description,
        "reference": txn.reference,
        "amount": txn.amount,
        "transaction_type": txn.transaction_type,
        "balance": txn.balance,
        "ledger": txn.ledger,
        "voucher_type": txn.voucher_type,
        "status": txn.status,
        "confidence": txn.confidence,
        "review_reason": txn.review_reason,
        "tally_voucher_number": txn.tally_voucher_number,
        "tally_response": txn.tally_response,
        "error_message": txn.error_message,
        "created_at": txn.created_at.strftime("%Y-%m-%d %H:%M:%S") if txn.created_at else None,
        "updated_at": txn.updated_at.strftime("%Y-%m-%d %H:%M:%S") if txn.updated_at else None,
        "timeline": timeline,
        "postings": [
            {
                "id": p.id,
                "voucher_type": p.voucher_type,
                "voucher_number": p.voucher_number,
                "status": p.status,
                "error_message": p.error_message,
                "request_payload": p.request_payload,
                "response_payload": p.response_payload,
                "posted_at": p.posted_at.strftime("%Y-%m-%d %H:%M:%S") if p.posted_at else None
            }
            for p in postings
        ]
    }

@router.put("/{txn_id}")
def update_transaction(txn_id: int, req: TransactionUpdateRequest, db: Session = Depends(get_db)):
    txn = db.query(Transaction).filter(Transaction.id == txn_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    if req.ledger is not None:
        txn.ledger = req.ledger
    if req.voucher_type is not None:
        txn.voucher_type = req.voucher_type
    if req.date is not None:
        txn.date = req.date
    if req.amount is not None:
        txn.amount = req.amount
    if req.description is not None:
        txn.description = req.description

    db.commit()
    db.refresh(txn)
    return {"success": True, "message": "Transaction updated successfully."}

@router.post("/{txn_id}/approve")
def approve_transaction(txn_id: int, req: ApproveRequest = None, db: Session = Depends(get_db)):
    try:
        ledger = req.ledger if req else None
        voucher = req.voucher_type if req else None
        txn = TransactionService.approve_transaction(db, txn_id, ledger, voucher)
        return {
            "success": True,
            "message": f"Transaction #{txn_id} approved.",
            "status": txn.status,
            "ledger": txn.ledger,
            "voucher_type": txn.voucher_type
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{txn_id}/reject")
def reject_transaction(txn_id: int, req: RejectRequest = None, db: Session = Depends(get_db)):
    try:
        reason = req.reason if req else "Rejected by user"
        txn = TransactionService.reject_transaction(db, txn_id, reason)
        return {"success": True, "message": f"Transaction #{txn_id} rejected.", "status": txn.status}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/bulk-approve")
def bulk_approve(req: BulkApproveRequest, db: Session = Depends(get_db)):
    result = TransactionService.bulk_approve(db, req.transaction_ids)
    return result
