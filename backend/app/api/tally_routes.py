from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db, Transaction, TallyPosting
from app.services.transaction_service import TransactionService
from app.tally import TallyClient, LedgerService
from app.config.settings import settings

router = APIRouter(prefix="/tally", tags=["TallyPrime Integration"])

class BulkPostRequest(BaseModel):
    transaction_ids: List[int]

class SinglePostRequest(BaseModel):
    bank_ledger: Optional[str] = None

class ModeToggleRequest(BaseModel):
    simulation: bool

@router.get("/status")
async def get_tally_status():
    client = TallyClient()
    status = await client.test_connection()
    return status

@router.post("/test-connection")
async def test_tally_connection():
    client = TallyClient()
    status = await client.test_connection()
    return status

@router.post("/post/{txn_id}")
async def post_single_transaction(txn_id: int, req: SinglePostRequest = None, db: Session = Depends(get_db)):
    try:
        bank_ledger = req.bank_ledger if req else None
        res = await TransactionService.post_to_tally(db, txn_id, bank_ledger)
        return res
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post to Tally: {str(e)}")

@router.post("/post-bulk")
async def post_bulk_transactions(req: BulkPostRequest, db: Session = Depends(get_db)):
    try:
        res = await TransactionService.post_bulk_to_tally(db, req.transaction_ids)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
def get_posting_history(limit: int = 50, db: Session = Depends(get_db)):
    postings = db.query(TallyPosting).order_by(desc(TallyPosting.posted_at)).limit(limit).all()
    return [
        {
            "id": p.id,
            "transaction_id": p.transaction_id,
            "voucher_type": p.voucher_type,
            "voucher_number": p.voucher_number,
            "status": p.status,
            "error_message": p.error_message,
            "request_payload": p.request_payload,
            "response_payload": p.response_payload,
            "posted_at": p.posted_at.strftime("%Y-%m-%d %H:%M:%S") if p.posted_at else None,
            "transaction": {
                "date": p.transaction.date if p.transaction else "",
                "description": p.transaction.description if p.transaction else "",
                "amount": p.transaction.amount if p.transaction else 0,
                "ledger": p.transaction.ledger if p.transaction else ""
            } if p.transaction else None
        }
        for p in postings
    ]

@router.get("/ledgers")
async def get_ledgers():
    service = LedgerService()
    ledgers = await service.get_ledgers()
    return ledgers

@router.post("/mode")
def set_tally_mode(req: ModeToggleRequest):
    settings.TALLY_SIMULATION_MODE = req.simulation
    return {
        "success": True,
        "simulation_mode": settings.TALLY_SIMULATION_MODE,
        "message": f"TallyPrime simulation mode is now {'ENABLED' if settings.TALLY_SIMULATION_MODE else 'DISABLED (Live Connection required)'}."
    }
