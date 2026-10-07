from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db, LedgerMapping
from app.mapping import map_transaction, match_rule_to_text, seed_default_mappings

router = APIRouter(prefix="/mappings", tags=["Ledger Mappings"])

class MappingCreateRequest(BaseModel):
    keyword: str
    ledger_name: str
    voucher_type: str = "Payment"
    priority: int = 1
    active: bool = True

class MappingUpdateRequest(BaseModel):
    keyword: Optional[str] = None
    ledger_name: Optional[str] = None
    voucher_type: Optional[str] = None
    priority: Optional[int] = None
    active: Optional[bool] = None

class TestMappingRequest(BaseModel):
    description: str
    transaction_type: str = "DEBIT"

@router.get("")
def list_mappings(db: Session = Depends(get_db)):
    seed_default_mappings(db)
    mappings = db.query(LedgerMapping).order_by(desc(LedgerMapping.priority), LedgerMapping.id.asc()).all()
    return [
        {
            "id": m.id,
            "keyword": m.keyword,
            "ledger_name": m.ledger_name,
            "voucher_type": m.voucher_type,
            "priority": m.priority,
            "active": m.active,
            "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
            "updated_at": m.updated_at.strftime("%Y-%m-%d %H:%M:%S") if m.updated_at else None,
        }
        for m in mappings
    ]

@router.post("")
def create_mapping(req: MappingCreateRequest, db: Session = Depends(get_db)):
    clean_keyword = req.keyword.strip()
    if not clean_keyword:
        raise HTTPException(status_code=400, detail="Keyword cannot be empty.")
    if not req.ledger_name.strip():
        raise HTTPException(status_code=400, detail="Ledger name cannot be empty.")

    mapping = LedgerMapping(
        keyword=clean_keyword,
        ledger_name=req.ledger_name.strip(),
        voucher_type=req.voucher_type,
        priority=req.priority,
        active=req.active
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return {"success": True, "message": "Mapping rule created.", "item": mapping}

@router.put("/{mapping_id}")
def update_mapping(mapping_id: int, req: MappingUpdateRequest, db: Session = Depends(get_db)):
    mapping = db.query(LedgerMapping).filter(LedgerMapping.id == mapping_id).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping rule not found.")

    if req.keyword is not None:
        mapping.keyword = req.keyword.strip()
    if req.ledger_name is not None:
        mapping.ledger_name = req.ledger_name.strip()
    if req.voucher_type is not None:
        mapping.voucher_type = req.voucher_type
    if req.priority is not None:
        mapping.priority = req.priority
    if req.active is not None:
        mapping.active = req.active

    db.commit()
    return {"success": True, "message": "Mapping rule updated."}

@router.delete("/{mapping_id}")
def delete_mapping(mapping_id: int, db: Session = Depends(get_db)):
    mapping = db.query(LedgerMapping).filter(LedgerMapping.id == mapping_id).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping rule not found.")
    db.delete(mapping)
    db.commit()
    return {"success": True, "message": f"Mapping rule #{mapping_id} deleted."}

@router.post("/test")
def test_mapping(req: TestMappingRequest, db: Session = Depends(get_db)):
    seed_default_mappings(db)
    mappings = db.query(LedgerMapping).filter(LedgerMapping.active == True).all()
    ledger, voucher, confidence, matched_keyword, reason = map_transaction(
        req.description,
        req.transaction_type,
        mappings
    )
    return {
        "description": req.description,
        "matched": matched_keyword is not None,
        "matched_keyword": matched_keyword,
        "suggested_ledger": ledger,
        "suggested_voucher": voucher,
        "confidence": confidence,
        "reason": reason
    }
