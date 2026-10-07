import React, { useState, useEffect } from 'react';
import { X, Check, Send, Ban, CheckCircle2, Clock, FileCode, AlertTriangle } from 'lucide-react';
import Badge from '../common/Badge';
import { formatCurrency, formatDate } from '../../utils/formatters';

export default function TransactionDrawer({
  isOpen,
  onClose,
  transaction,
  ledgers = [],
  onApprove,
  onPost,
  onReject,
  onUpdate
}) {
  const [selectedLedger, setSelectedLedger] = useState('');
  const [selectedVoucher, setSelectedVoucher] = useState('Payment');
  const [isEditing, setIsEditing] = useState(false);
  const [showRawXml, setShowRawXml] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (transaction) {
      setSelectedLedger(transaction.ledger || '');
      setSelectedVoucher(transaction.voucher_type || (transaction.transaction_type === 'CREDIT' ? 'Receipt' : 'Payment'));
      setIsEditing(false);
    }
  }, [transaction]);

  if (!isOpen || !transaction) return null;

  const isDebit = transaction.transaction_type === 'DEBIT';

  const handleSaveDecision = async () => {
    setActionLoading(true);
    try {
      await onUpdate?.(transaction.id, {
        ledger: selectedLedger,
        voucher_type: selectedVoucher
      });
      setIsEditing(false);
    } finally {
      setActionLoading(false);
    }
  };

  const handleApprove = async () => {
    setActionLoading(true);
    try {
      await onApprove?.(transaction.id, selectedLedger, selectedVoucher);
    } finally {
      setActionLoading(false);
    }
  };

  const handlePost = async () => {
    setActionLoading(true);
    try {
      await onPost?.(transaction.id);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    setActionLoading(true);
    try {
      await onReject?.(transaction.id);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <>
      <div className="drawer-overlay" onClick={onClose} />
      <div className="drawer">
        {/* Drawer Header */}
        <div style={{
          padding: '16px 20px',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: '600' }}>Transaction #{transaction.id}</h3>
              <Badge status={transaction.status} />
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Imported from {transaction.import_file || 'Statement Batch'}
            </div>
          </div>
          <button 
            onClick={onClose} 
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Drawer Content */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Bank Data Card */}
          <div className="card" style={{ padding: '16px' }}>
            <h4 style={{ fontSize: '13px', fontWeight: '600', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '12px' }}>
              Bank Statement Data
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '13px' }}>
              <div>
                <span style={{ color: 'var(--text-muted)', fontSize: '11px', display: 'block' }}>Date</span>
                <strong>{formatDate(transaction.date)}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)', fontSize: '11px', display: 'block' }}>Amount</span>
                <span className={isDebit ? 'amount-debit' : 'amount-credit'}>
                  {isDebit ? '-' : '+'}{formatCurrency(transaction.amount)} ({transaction.transaction_type})
                </span>
              </div>
              <div style={{ gridColumn: 'span 2' }}>
                <span style={{ color: 'var(--text-muted)', fontSize: '11px', display: 'block' }}>Narration / Description</span>
                <div style={{ background: '#f8fafc', padding: '8px 10px', borderRadius: '4px', marginTop: '4px', wordBreak: 'break-word' }}>
                  {transaction.description}
                </div>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)', fontSize: '11px', display: 'block' }}>Reference No</span>
                <span>{transaction.reference || 'None'}</span>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)', fontSize: '11px', display: 'block' }}>Bank Closing Balance</span>
                <span>{transaction.balance !== null ? formatCurrency(transaction.balance) : '—'}</span>
              </div>
            </div>
          </div>

          {/* Accounting Decision Card */}
          <div className="card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h4 style={{ fontSize: '13px', fontWeight: '600', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                Accounting Decision
              </h4>
              <button 
                className="btn btn-secondary btn-sm"
                onClick={() => setIsEditing(!isEditing)}
              >
                {isEditing ? 'Cancel Edit' : 'Change Ledger / Voucher'}
              </button>
            </div>

            {isEditing ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div className="form-group" style={{ margin: 0 }}>
                  <label className="form-label">Tally Ledger</label>
                  <select
                    className="select"
                    value={selectedLedger}
                    onChange={(e) => setSelectedLedger(e.target.value)}
                  >
                    <option value="">-- Select Tally Ledger --</option>
                    {ledgers.map((l) => (
                      <option key={l.name} value={l.name}>
                        {l.name} ({l.group})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group" style={{ margin: 0 }}>
                  <label className="form-label">Voucher Type</label>
                  <select
                    className="select"
                    value={selectedVoucher}
                    onChange={(e) => setSelectedVoucher(e.target.value)}
                  >
                    <option value="Payment">Payment</option>
                    <option value="Receipt">Receipt</option>
                    <option value="Contra">Contra</option>
                    <option value="Journal">Journal</option>
                  </select>
                </div>

                <button 
                  className="btn btn-primary btn-sm"
                  onClick={handleSaveDecision}
                  disabled={actionLoading}
                >
                  Save Accounting Decision
                </button>
              </div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '13px' }}>
                <div>
                  <span style={{ color: 'var(--text-muted)', fontSize: '11px', display: 'block' }}>Target Ledger</span>
                  <strong style={{ color: transaction.ledger ? 'var(--text-primary)' : 'var(--danger)' }}>
                    {transaction.ledger || '⚠ Unassigned'}
                  </strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)', fontSize: '11px', display: 'block' }}>Voucher Type</span>
                  <strong>{transaction.voucher_type || '—'}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)', fontSize: '11px', display: 'block' }}>Rule Confidence</span>
                  <span>{transaction.confidence ? `${Math.round(transaction.confidence * 100)}%` : '0%'}</span>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)', fontSize: '11px', display: 'block' }}>Tally Voucher #</span>
                  <span>{transaction.tally_voucher_number || '— Pending Posting —'}</span>
                </div>
              </div>
            )}

            {transaction.review_reason && (
              <div style={{
                marginTop: '12px',
                padding: '8px 12px',
                backgroundColor: '#fffbeb',
                border: '1px solid #fde68a',
                borderRadius: '4px',
                fontSize: '12px',
                color: '#92400e',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <AlertTriangle size={14} />
                <span>{transaction.review_reason}</span>
              </div>
            )}
          </div>

          {/* Audit Timeline */}
          <div className="card" style={{ padding: '16px' }}>
            <h4 style={{ fontSize: '13px', fontWeight: '600', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '14px' }}>
              Audit Timeline
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', position: 'relative' }}>
              {(transaction.timeline || []).map((step, idx) => (
                <div key={idx} style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                  <div style={{
                    width: '20px',
                    height: '20px',
                    borderRadius: '50%',
                    backgroundColor: 'var(--success-bg)',
                    color: 'var(--success)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '10px',
                    fontWeight: '700',
                    flexShrink: 0
                  }}>
                    ✓
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: '600', fontSize: '13px' }}>{step.step}</div>
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{step.details}</div>
                    {step.timestamp && (
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{step.timestamp}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Tally XML Response (Collapsible) */}
          {(transaction.tally_response || transaction.error_message) && (
            <div className="card" style={{ padding: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h4 style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-muted)' }}>
                  TallyPrime Payload / Response
                </h4>
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => setShowRawXml(!showRawXml)}
                >
                  <FileCode size={12} /> {showRawXml ? 'Hide XML' : 'View XML'}
                </button>
              </div>

              {showRawXml && (
                <pre style={{
                  marginTop: '10px',
                  background: '#0f172a',
                  color: '#38bdf8',
                  padding: '12px',
                  borderRadius: '4px',
                  fontSize: '11px',
                  overflowX: 'auto',
                  maxHeight: '200px'
                }}>
                  {transaction.tally_response || transaction.error_message}
                </pre>
              )}
            </div>
          )}
        </div>

        {/* Drawer Footer Actions */}
        <div style={{
          padding: '16px 20px',
          borderTop: '1px solid var(--border-color)',
          display: 'flex',
          justifyContent: 'flex-end',
          gap: '10px',
          backgroundColor: '#f8fafc'
        }}>
          {transaction.status !== 'REJECTED' && (
            <button 
              className="btn btn-danger btn-sm" 
              onClick={handleReject}
              disabled={actionLoading}
            >
              <Ban size={14} /> Reject
            </button>
          )}

          {transaction.status === 'REVIEW_REQUIRED' && (
            <button 
              className="btn btn-success" 
              onClick={handleApprove}
              disabled={actionLoading || !selectedLedger}
            >
              <Check size={14} /> Approve
            </button>
          )}

          {(transaction.status === 'APPROVED' || transaction.status === 'FAILED') && (
            <button 
              className="btn btn-primary" 
              onClick={handlePost}
              disabled={actionLoading}
            >
              <Send size={14} /> Post to TallyPrime
            </button>
          )}
        </div>
      </div>
    </>
  );
}
