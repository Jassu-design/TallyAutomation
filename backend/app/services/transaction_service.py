import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc

from app.config.settings import settings
from app.database.models import ImportBatch, Transaction, LedgerMapping, TallyPosting, AuditLog
from app.ingestion import parse_bank_statement
from app.processing import normalize_transaction, validate_transaction, generate_transaction_hash
from app.mapping import map_transaction, seed_default_mappings
from app.tally import TallyClient, build_voucher_xml, build_sales_invoice_xml

logger = logging.getLogger(__name__)

class TransactionService:
    @staticmethod
    def process_statement_file(
        db: Session,
        file_path: str,
        original_filename: str,
        selected_bank: Optional[str] = None
    ) -> ImportBatch:
        """
        Full statement ingestion pipeline:
        File -> Read -> Normalize -> Validate -> Duplicate Check -> Map -> Classify -> Persist
        """
        # Ensure default mappings exist in DB
        seed_default_mappings(db)
        
        # 1. Read statement
        detected_bank, raw_records = parse_bank_statement(file_path, selected_bank)

        # 2. Initialize Import Batch
        batch = ImportBatch(
            filename=original_filename,
            bank_name=detected_bank,
            total_transactions=len(raw_records),
            status="PROCESSING"
        )
        db.add(batch)
        db.flush()

        # 3. Fetch active rules
        mappings = db.query(LedgerMapping).filter(LedgerMapping.active == True).all()

        total_cnt = len(raw_records)
        review_cnt = 0
        failed_cnt = 0
        duplicate_cnt = 0
        approved_cnt = 0

        created_txns: List[Transaction] = []
        batch_hashes = set()

        for raw_rec in raw_records:
            # Step A: Normalize
            norm = normalize_transaction(raw_rec)
            
            # Step B: Validate
            is_valid, validation_errors = validate_transaction(norm)

            # Step C: Duplicate Check Hash
            txn_hash = generate_transaction_hash(detected_bank, norm)
            
            # Check duplicate against DB or current batch
            existing_db_txn = db.query(Transaction).filter(Transaction.transaction_hash == txn_hash).first()
            is_duplicate = (existing_db_txn is not None) or (txn_hash in batch_hashes)
            batch_hashes.add(txn_hash)

            # Step D: Mapping & Voucher Classification
            if raw_rec.get("_is_invoice"):
                ledger = raw_rec.get("_suggested_ledger")
                voucher = raw_rec.get("_suggested_voucher", "Sales")
                confidence = 0.99
                matched_keyword = "TAX INVOICE"
                map_reason = f"Detected GST Tax Invoice {raw_rec.get('reference')} mapped to Buyer Ledger '{ledger}'"
            else:
                ledger, voucher, confidence, matched_keyword, map_reason = map_transaction(
                    norm.get("description", ""),
                    norm.get("transaction_type", "DEBIT"),
                    mappings
                )

            # Step E: Determine Status
            if not is_valid:
                status = "FAILED"
                review_reason = "; ".join(validation_errors)
                failed_cnt += 1
            elif is_duplicate:
                status = "DUPLICATE"
                review_reason = "Duplicate transaction already exists in database or batch"
                duplicate_cnt += 1
            elif ledger is None or confidence < settings.AUTO_APPROVE_THRESHOLD:
                status = "REVIEW_REQUIRED"
                review_reason = map_reason or "Confidence below threshold, verification required"
                review_cnt += 1
            else:
                # Meets criteria for auto-approval
                status = "APPROVED"
                review_reason = None
                approved_cnt += 1

            inv_json = json.dumps(raw_rec.get("_invoice_data")) if raw_rec.get("_is_invoice") else None

            txn = Transaction(
                import_id=batch.id,
                transaction_hash=txn_hash,
                date=norm["date"] or datetime.utcnow().strftime("%Y-%m-%d"),
                description=norm["description"],
                reference=norm["reference"],
                amount=norm["amount"],
                transaction_type=norm["transaction_type"],
                balance=norm["balance"],
                ledger=ledger,
                voucher_type=voucher,
                status=status,
                confidence=confidence,
                review_reason=review_reason,
                invoice_data=inv_json
            )
            created_txns.append(txn)

        db.add_all(created_txns)

        # Update batch summary
        batch.processed_transactions = total_cnt
        batch.review_transactions = review_cnt
        batch.failed_transactions = failed_cnt
        batch.duplicate_transactions = duplicate_cnt
        batch.status = "COMPLETED"

        # Audit log
        audit = AuditLog(
            event_type="IMPORT",
            entity_type="ImportBatch",
            entity_id=batch.id,
            message=f"Statement {original_filename} processed: {total_cnt} txns ({approved_cnt} approved, {review_cnt} review, {duplicate_cnt} duplicates, {failed_cnt} failed)"
        )
        db.add(audit)
        db.commit()
        db.refresh(batch)
        return batch

    @staticmethod
    def approve_transaction(db: Session, txn_id: int, ledger: Optional[str] = None, voucher_type: Optional[str] = None) -> Transaction:
        txn = db.query(Transaction).filter(Transaction.id == txn_id).first()
        if not txn:
            raise ValueError(f"Transaction #{txn_id} not found.")

        if ledger:
            txn.ledger = ledger
        if voucher_type:
            txn.voucher_type = voucher_type

        if not txn.ledger:
            raise ValueError("Cannot approve transaction without an assigned Tally Ledger.")
        if not txn.voucher_type:
            raise ValueError("Cannot approve transaction without a Voucher Type.")

        prev_status = txn.status
        txn.status = "APPROVED"
        txn.review_reason = None
        txn.confidence = 1.0

        # Adjust batch count if moving from REVIEW_REQUIRED
        if prev_status == "REVIEW_REQUIRED" and txn.import_batch:
            txn.import_batch.review_transactions = max(0, txn.import_batch.review_transactions - 1)

        db.add(AuditLog(
            event_type="APPROVAL",
            entity_type="Transaction",
            entity_id=txn.id,
            message=f"Transaction #{txn.id} approved for posting to ledger '{txn.ledger}' with voucher '{txn.voucher_type}'."
        ))
        db.commit()
        db.refresh(txn)
        return txn

    @staticmethod
    def reject_transaction(db: Session, txn_id: int, reason: Optional[str] = None) -> Transaction:
        txn = db.query(Transaction).filter(Transaction.id == txn_id).first()
        if not txn:
            raise ValueError(f"Transaction #{txn_id} not found.")

        txn.status = "REJECTED"
        txn.review_reason = reason or "Rejected by user"

        db.add(AuditLog(
            event_type="REJECTION",
            entity_type="Transaction",
            entity_id=txn.id,
            message=f"Transaction #{txn.id} rejected by user. Reason: {txn.review_reason}"
        ))
        db.commit()
        db.refresh(txn)
        return txn

    @staticmethod
    def bulk_approve(db: Session, txn_ids: List[int]) -> Dict[str, Any]:
        txns = db.query(Transaction).filter(Transaction.id.in_(txn_ids)).all()
        approved = []
        skipped = []

        for txn in txns:
            if txn.status in ["POSTED", "POSTING"]:
                skipped.append({"id": txn.id, "reason": "Already posted or posting"})
                continue
            if not txn.ledger or not txn.voucher_type:
                skipped.append({"id": txn.id, "reason": "Missing ledger or voucher type"})
                continue

            prev_status = txn.status
            txn.status = "APPROVED"
            txn.review_reason = None
            txn.confidence = 1.0
            if prev_status == "REVIEW_REQUIRED" and txn.import_batch:
                txn.import_batch.review_transactions = max(0, txn.import_batch.review_transactions - 1)
            approved.append(txn.id)

        db.commit()
        return {"approved_count": len(approved), "approved_ids": approved, "skipped": skipped}

    @staticmethod
    async def post_to_tally(
        db: Session,
        txn_id: int,
        bank_ledger: Optional[str] = None
    ) -> Dict[str, Any]:
        txn = db.query(Transaction).filter(Transaction.id == txn_id).first()
        if not txn:
            raise ValueError(f"Transaction #{txn_id} not found.")

        if txn.status == "POSTED":
            return {
                "success": True,
                "already_posted": True,
                "voucher_number": txn.tally_voucher_number,
                "message": "Transaction is already posted to TallyPrime."
            }

        if not txn.ledger or not txn.voucher_type:
            raise ValueError("Transaction missing Ledger or Voucher Type.")

        effective_bank_ledger = bank_ledger or settings.DEFAULT_BANK_LEDGER
        txn.status = "POSTING"
        db.commit()

        client = TallyClient()
        conn_info = await client.test_connection()
        effective_company = conn_info.get("company") or client.company or settings.TALLY_COMPANY

        # Auto-ensure ledgers exist in live Tally
        if not client.simulation and conn_info.get("connected"):
            if txn.voucher_type == "Sales":
                from scripts.create_masters import create_masters_if_needed
                try:
                    create_masters_if_needed(effective_company)
                except Exception as me:
                    logger.warning(f"Could not auto-create masters: {me}")

        # Build XML
        if txn.voucher_type == "Sales":
            inv_data = {}
            if getattr(txn, "invoice_data", None):
                try:
                    inv_data = json.loads(txn.invoice_data)
                except Exception:
                    inv_data = {}

            xml_payload = build_sales_invoice_xml(
                company_name=effective_company,
                invoice_no=txn.reference or f"INV-{txn.id}",
                date_str=txn.date,
                buyer_name=txn.ledger or "Sundry Debtor",
                buyer_gstin=inv_data.get("buyer_gstin", ""),
                sub_total=inv_data.get("sub_total", txn.amount),
                cgst_amount=inv_data.get("cgst_amount", 0.0),
                sgst_amount=inv_data.get("sgst_amount", 0.0),
                igst_amount=inv_data.get("igst_amount", 0.0),
                round_off=inv_data.get("round_off", 0.0),
                total_amount=txn.amount,
                items=inv_data.get("items", []),
                narration=f"Tax Invoice {txn.reference} to {txn.ledger}",
                irn=inv_data.get("irn"),
                eway_bill_no=inv_data.get("eway_bill_no"),
                vehicle_no=inv_data.get("vehicle_no")
            )
        else:
            xml_payload = build_voucher_xml(
                company_name=effective_company,
                voucher_type=txn.voucher_type,
                date_str=txn.date,
                amount=txn.amount,
                transaction_type=txn.transaction_type,
                bank_ledger=effective_bank_ledger,
                party_ledger=txn.ledger,
                narration=f"{txn.description} (Ref: {txn.reference or 'N/A'})",
                reference=txn.reference
            )

        result = await client.post_voucher(xml_payload, txn.voucher_type)

        posting_record = TallyPosting(
            transaction_id=txn.id,
            voucher_type=txn.voucher_type,
            voucher_number=result.get("voucher_number"),
            request_payload=xml_payload,
            response_payload=result.get("raw_response"),
            status="SUCCESS" if result["success"] else "FAILED",
            error_message=result.get("error")
        )
        db.add(posting_record)

        if result["success"]:
            txn.status = "POSTED"
            txn.tally_voucher_number = result.get("voucher_number")
            txn.tally_response = result.get("raw_response")
            txn.error_message = None
            if txn.import_batch:
                txn.import_batch.posted_transactions += 1
            audit_msg = f"Transaction #{txn.id} posted successfully to TallyPrime. Voucher: {txn.tally_voucher_number}"
        else:
            txn.status = "FAILED"
            txn.error_message = result.get("error")
            txn.tally_response = result.get("raw_response")
            audit_msg = f"Failed to post Transaction #{txn.id} to TallyPrime: {result.get('error')}"

        db.add(AuditLog(
            event_type="POSTING",
            entity_type="Transaction",
            entity_id=txn.id,
            message=audit_msg
        ))
        db.commit()
        db.refresh(txn)

        return {
            "success": result["success"],
            "voucher_number": txn.tally_voucher_number,
            "error": txn.error_message,
            "raw_response": txn.tally_response
        }

    @staticmethod
    async def post_bulk_to_tally(db: Session, txn_ids: List[int]) -> Dict[str, Any]:
        txns = db.query(Transaction).filter(
            Transaction.id.in_(txn_ids),
            Transaction.status.in_(["APPROVED", "VALIDATED"])
        ).all()

        results = []
        success_cnt = 0
        failed_cnt = 0

        for txn in txns:
            res = await TransactionService.post_to_tally(db, txn.id)
            if res["success"]:
                success_cnt += 1
            else:
                failed_cnt += 1
            results.append({"transaction_id": txn.id, "result": res})

        return {
            "total": len(txns),
            "success_count": success_cnt,
            "failed_count": failed_cnt,
            "details": results
        }
