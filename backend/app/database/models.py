from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.database import Base

def utc_now():
    return datetime.now(timezone.utc)


class ImportBatch(Base):
    __tablename__ = "imports"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    bank_name = Column(String(100), default="Auto Detect")
    total_transactions = Column(Integer, default=0)
    processed_transactions = Column(Integer, default=0)
    review_transactions = Column(Integer, default=0)
    failed_transactions = Column(Integer, default=0)
    duplicate_transactions = Column(Integer, default=0)
    posted_transactions = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=utc_now)
    status = Column(String(50), default="PROCESSING")  # PROCESSING, COMPLETED, FAILED

    transactions = relationship("Transaction", back_populates="import_batch", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    import_id = Column(Integer, ForeignKey("imports.id", ondelete="CASCADE"), nullable=True)
    transaction_hash = Column(String(64), index=True, nullable=False)
    date = Column(String(20), nullable=False, index=True)  # YYYY-MM-DD
    description = Column(Text, nullable=False)
    reference = Column(String(100), nullable=True, index=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(10), nullable=False)  # DEBIT, CREDIT
    balance = Column(Float, nullable=True)
    
    # Accounting Mapping
    ledger = Column(String(255), nullable=True)
    voucher_type = Column(String(50), nullable=True)  # Payment, Receipt, Contra, Journal
    
    # Processing state
    # IMPORTED, PENDING, VALIDATED, REVIEW_REQUIRED, APPROVED, POSTING, POSTED, FAILED, DUPLICATE, REJECTED
    status = Column(String(50), default="PENDING", index=True)
    confidence = Column(Float, default=0.0)
    review_reason = Column(String(255), nullable=True)
    
    # Tally info
    tally_voucher_number = Column(String(100), nullable=True)
    tally_response = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    invoice_data = Column(Text, nullable=True)  # JSON-encoded GST Tax Invoice & inventory metadata
    
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    import_batch = relationship("ImportBatch", back_populates="transactions")
    postings = relationship("TallyPosting", back_populates="transaction", cascade="all, delete-orphan")


class LedgerMapping(Base):
    __tablename__ = "ledger_mappings"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(255), nullable=False, index=True)
    ledger_name = Column(String(255), nullable=False)
    voucher_type = Column(String(50), nullable=False)  # Payment, Receipt, Contra, Journal
    priority = Column(Integer, default=1)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)


class TallyPosting(Base):
    __tablename__ = "tally_postings"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    voucher_type = Column(String(50), nullable=False)
    voucher_number = Column(String(100), nullable=True)
    request_payload = Column(Text, nullable=True)
    response_payload = Column(Text, nullable=True)
    status = Column(String(50), nullable=False)  # SUCCESS, FAILED
    error_message = Column(Text, nullable=True)
    posted_at = Column(DateTime, default=utc_now)

    transaction = relationship("Transaction", back_populates="postings")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False)  # IMPORT, VALIDATION, MAPPING, APPROVAL, POSTING, ERROR
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=True)
    message = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
