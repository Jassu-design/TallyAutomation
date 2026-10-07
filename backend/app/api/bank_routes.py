import os
import shutil
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db, ImportBatch, Transaction
from app.services.transaction_service import TransactionService
from app.config.settings import settings

router = APIRouter(prefix="", tags=["Bank & Imports"])

@router.post("/bank/upload")
async def upload_statement(
    file: UploadFile = File(...),
    bank: Optional[str] = Form("Auto Detect"),
    company: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Uploads and processes an Excel (.xlsx, .xls), CSV (.csv), or PDF (.pdf) bank statement file.
    """
    # Validate extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".csv", ".xlsx", ".xls", ".pdf"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Only .csv, .xlsx, .xls, and .pdf files are supported."
        )


    # Sanitize and save file
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    saved_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    try:
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Process statement through ingestion & validation engine
        batch = TransactionService.process_statement_file(
            db=db,
            file_path=saved_path,
            original_filename=file.filename,
            selected_bank=bank
        )

        return {
            "success": True,
            "message": f"Successfully processed '{file.filename}'.",
            "batch_id": batch.id,
            "filename": batch.filename,
            "bank_name": batch.bank_name,
            "summary": {
                "total_transactions": batch.total_transactions,
                "valid_transactions": batch.processed_transactions - batch.review_transactions - batch.failed_transactions - batch.duplicate_transactions,
                "review_required": batch.review_transactions,
                "duplicates": batch.duplicate_transactions,
                "failed": batch.failed_transactions
            }
        }
    except Exception as e:
        if os.path.exists(saved_path):
            try:
                os.remove(saved_path)
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f"Failed to process statement: {str(e)}")

@router.post("/bank/sample-pdf")
def process_sample_pdf(db: Session = Depends(get_db)):
    """
    Directly processes the built-in demo HDFC Bank statement PDF file for instant testing.
    """
    demo_pdf_path = "C:/Users/hp/.gemini/antigravity/scratch/bank-tally-automation/data/sample_bank_statements/demo_bank_statement.pdf"
    if not os.path.exists(demo_pdf_path):
        from generate_demo_pdf import generate_pdf
        generate_pdf()

    unique_filename = f"{uuid.uuid4().hex}_demo_bank_statement.pdf"
    saved_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    shutil.copyfile(demo_pdf_path, saved_path)

    batch = TransactionService.process_statement_file(
        db=db,
        file_path=saved_path,
        original_filename="demo_bank_statement.pdf",
        selected_bank="HDFC Bank"
    )

    return {
        "success": True,
        "message": "Successfully processed demo PDF statement 'demo_bank_statement.pdf'.",
        "batch_id": batch.id,
        "filename": batch.filename,
        "bank_name": batch.bank_name,
        "summary": {
            "total_transactions": batch.total_transactions,
            "valid_transactions": batch.processed_transactions - batch.review_transactions - batch.failed_transactions - batch.duplicate_transactions,
            "review_required": batch.review_transactions,
            "duplicates": batch.duplicate_transactions,
            "failed": batch.failed_transactions
        }
    }


@router.post("/bank/sample-invoice")
def process_sample_invoice(db: Session = Depends(get_db)):
    """
    Directly processes the Shree Ram Papad GST Tax Invoice PDF for instant testing and verification.
    """
    invoice_path = "C:/Users/hp/.gemini/antigravity/scratch/bank-tally-automation/data/sample_bank_statements/shree_ram_papad_invoice.pdf"
    if not os.path.exists(invoice_path):
        from scripts.generate_sample_tax_invoice import generate_shree_ram_papad_invoice
        generate_shree_ram_papad_invoice(invoice_path)

    unique_filename = f"{uuid.uuid4().hex}_shree_ram_papad_invoice.pdf"
    saved_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    shutil.copyfile(invoice_path, saved_path)

    batch = TransactionService.process_statement_file(
        db=db,
        file_path=saved_path,
        original_filename="shree_ram_papad_invoice.pdf",
        selected_bank="Auto Detect"
    )

    return {
        "success": True,
        "message": "Successfully processed GST Tax Invoice 'shree_ram_papad_invoice.pdf'.",
        "batch_id": batch.id,
        "filename": batch.filename,
        "bank_name": batch.bank_name,
        "summary": {
            "total_transactions": batch.total_transactions,
            "valid_transactions": batch.processed_transactions - batch.review_transactions - batch.failed_transactions - batch.duplicate_transactions,
            "review_required": batch.review_transactions,
            "duplicates": batch.duplicate_transactions,
            "failed": batch.failed_transactions
        }
    }


@router.get("/imports")
def list_imports(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    batches = db.query(ImportBatch).order_by(ImportBatch.uploaded_at.desc()).offset(skip).limit(limit).all()
    total = db.query(ImportBatch).count()
    return {
        "total": total,
        "items": [
            {
                "id": b.id,
                "filename": b.filename,
                "bank_name": b.bank_name,
                "total_transactions": b.total_transactions,
                "processed_transactions": b.processed_transactions,
                "review_transactions": b.review_transactions,
                "failed_transactions": b.failed_transactions,
                "duplicate_transactions": b.duplicate_transactions,
                "posted_transactions": b.posted_transactions,
                "uploaded_at": b.uploaded_at.strftime("%Y-%m-%d %H:%M:%S") if b.uploaded_at else "",
                "status": b.status
            }
            for b in batches
        ]
    }

@router.get("/imports/{batch_id}")
def get_import_details(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail=f"Import batch #{batch_id} not found.")

    txns = db.query(Transaction).filter(Transaction.import_id == batch_id).all()
    
    status_counts = {}
    for t in txns:
        status_counts[t.status] = status_counts.get(t.status, 0) + 1

    return {
        "id": batch.id,
        "filename": batch.filename,
        "bank_name": batch.bank_name,
        "total_transactions": batch.total_transactions,
        "processed_transactions": batch.processed_transactions,
        "review_transactions": batch.review_transactions,
        "failed_transactions": batch.failed_transactions,
        "duplicate_transactions": batch.duplicate_transactions,
        "posted_transactions": batch.posted_transactions,
        "uploaded_at": batch.uploaded_at.strftime("%Y-%m-%d %H:%M:%S") if batch.uploaded_at else "",
        "status": batch.status,
        "breakdown": status_counts,
        "transactions_preview": [
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
            for t in txns[:50]
        ]
    }

@router.delete("/imports/{batch_id}")
def delete_import_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found.")
    db.delete(batch)
    db.commit()
    return {"success": True, "message": f"Import batch #{batch_id} deleted."}
