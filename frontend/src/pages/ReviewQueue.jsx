import React, { useState, useEffect } from 'react';
import PageHeader from '../components/layout/PageHeader';
import LoadingState from '../components/common/LoadingState';
import EmptyState from '../components/common/EmptyState';
import Badge from '../components/common/Badge';
import Modal from '../components/common/Modal';
import { TransactionAPI, TallyAPI } from '../services/api';
import { useToast } from '../hooks/useToast';
import { formatCurrency, formatDate } from '../utils/formatters';
import { Check, Edit2, Ban, CheckCheck, AlertTriangle, ShieldAlert } from 'lucide-react';

export default function ReviewQueue() {
  const { showSuccess, showError, showWarning } = useToast();
  const [items, setItems] = useState([]);
  const [totalQueue, setTotalQueue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState('all');

  // Edit Modal State
  const [editingItem, setEditingItem] = useState(null);
  const [editLedger, setEditLedger] = useState('');
  const [editVoucher, setEditVoucher] = useState('Payment');
  const [ledgers, setLedgers] = useState([]);

  // Bulk Approve Modal State
  const [isBulkModalOpen, setIsBulkModalOpen] = useState(false);
  const [bulkProcessing, setBulkProcessing] = useState(false);

  const fetchQueue = async (filter = activeFilter) => {
    try {
      setLoading(true);
      const res = await TransactionAPI.getReviewQueue(filter);
      setItems(res.items || []);
      setTotalQueue(res.total_in_queue || 0);
    } catch (err) {
      showError(err.message || 'Failed to load review queue.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue(activeFilter);
  }, [activeFilter]);

  useEffect(() => {
    const fetchLedgers = async () => {
      try {
        const list = await TallyAPI.getLedgers();
        setLedgers(list || []);
      } catch (e) {
        console.error(e);
      }
    };
    fetchLedgers();
  }, []);

  const handleQuickApprove = async (id, ledger, voucher) => {
    if (!ledger) {
      showWarning('Please assign a ledger before approving.');
      const item = items.find((i) => i.id === id);
      openEditModal(item);
      return;
    }
    try {
      await TransactionAPI.approveTransaction(id, { ledger, voucher_type: voucher });
      showSuccess(`Transaction #${id} approved!`);
      fetchQueue(activeFilter);
    } catch (err) {
      showError(err.message || 'Approval failed.');
    }
  };

  const handleReject = async (id) => {
    try {
      await TransactionAPI.rejectTransaction(id);
      showSuccess(`Transaction #${id} rejected.`);
      fetchQueue(activeFilter);
    } catch (err) {
      showError(err.message || 'Rejection failed.');
    }
  };

  const openEditModal = (item) => {
    setEditingItem(item);
    setEditLedger(item.ledger || '');
    setEditVoucher(item.voucher_type || (item.transaction_type === 'CREDIT' ? 'Receipt' : 'Payment'));
  };

  const handleSaveEdit = async () => {
    if (!editLedger) {
      showError('Please select a target Tally ledger.');
      return;
    }
    try {
      await TransactionAPI.approveTransaction(editingItem.id, {
        ledger: editLedger,
        voucher_type: editVoucher
      });
      showSuccess(`Transaction #${editingItem.id} updated and approved.`);
      setEditingItem(null);
      fetchQueue(activeFilter);
    } catch (err) {
      showError(err.message || 'Failed to save decision.');
    }
  };

  const handleExecuteBulkApprove = async () => {
    setBulkProcessing(true);
    try {
      // Filter out duplicate or unassigned items for safety
      const approvableIds = items
        .filter((i) => i.status !== 'DUPLICATE' && i.ledger)
        .map((i) => i.id);

      if (approvableIds.length === 0) {
        showWarning('No items with assigned ledgers are ready for bulk approval.');
        setIsBulkModalOpen(false);
        return;
      }

      const res = await TransactionAPI.bulkApprove(approvableIds);
      showSuccess(`${res.approved_count} transactions approved.`);
      setIsBulkModalOpen(false);
      fetchQueue(activeFilter);
    } catch (err) {
      showError(err.message || 'Bulk approval failed.');
    } finally {
      setBulkProcessing(false);
    }
  };

  const approvableCount = items.filter((i) => i.status !== 'DUPLICATE' && i.ledger).length;

  return (
    <div>
      <PageHeader
        title="Review Queue"
        subtitle="Uncertain accounting decisions requiring human confirmation before posting"
        actions={
          approvableCount > 0 && (
            <button 
              className="btn btn-primary"
              onClick={() => setIsBulkModalOpen(true)}
            >
              <CheckCheck size={16} />
              Approve Valid ({approvableCount})
            </button>
          )
        }
      />

      {/* Filter Chips */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', flexWrap: 'wrap' }}>
        {[
          { id: 'all', label: `All Items (${totalQueue})` },
          { id: 'unknown_ledger', label: 'Unknown Ledger' },
          { id: 'low_confidence', label: 'Low Confidence' },
          { id: 'duplicate', label: 'Duplicates' },
        ].map((chip) => (
          <button
            key={chip.id}
            onClick={() => setActiveFilter(chip.id)}
            style={{
              padding: '6px 14px',
              borderRadius: 'var(--radius-full)',
              fontSize: '12px',
              fontWeight: '500',
              border: '1px solid',
              borderColor: activeFilter === chip.id ? 'var(--primary)' : 'var(--border-color)',
              backgroundColor: activeFilter === chip.id ? 'var(--primary-light)' : 'white',
              color: activeFilter === chip.id ? 'var(--primary)' : 'var(--text-secondary)',
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            {chip.label}
          </button>
        ))}
      </div>

      {loading ? (
        <LoadingState message="Loading review queue items..." />
      ) : items.length === 0 ? (
        <div className="card">
          <EmptyState
            title="Review Queue is Clear!"
            description="No bank transactions currently require human review. All records have either been approved, posted, or resolved."
          />
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {items.map((item) => {
            const isDebit = item.transaction_type === 'DEBIT';
            const isDuplicate = item.status === 'DUPLICATE';

            return (
              <div
                key={item.id}
                className="card"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '16px 20px',
                  borderLeft: `4px solid ${isDuplicate ? 'var(--duplicate)' : 'var(--warning)'}`,
                  gap: '16px'
                }}
              >
                {/* Left Info */}
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
                    <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                      #{item.id} • {formatDate(item.date)}
                    </span>
                    <Badge status={item.status} />
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                      Ref: {item.reference || 'N/A'}
                    </span>
                  </div>

                  <h4 style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)' }}>
                    {item.description}
                  </h4>

                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    marginTop: '6px',
                    fontSize: '12px',
                    color: '#92400e'
                  }}>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                      <AlertTriangle size={13} />
                      <strong>Reason:</strong> {item.review_reason || 'Requires human verification'}
                    </span>
                  </div>
                </div>

                {/* Center: Suggested Mapping */}
                <div style={{ textAlign: 'right', minWidth: '180px' }}>
                  <div className={isDebit ? 'amount-debit' : 'amount-credit'} style={{ fontSize: '16px' }}>
                    {isDebit ? '-' : '+'}{formatCurrency(item.amount)}
                  </div>
                  <div style={{ fontSize: '12px', fontWeight: '600', marginTop: '2px', color: item.ledger ? 'var(--text-primary)' : 'var(--danger)' }}>
                    {item.ledger || '⚠ Unknown Ledger'}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                    {item.voucher_type} • Confidence: {Math.round((item.confidence || 0) * 100)}%
                  </div>
                </div>

                {/* Right: Actions */}
                <div style={{ display: 'flex', gap: '8px' }}>
                  {!isDuplicate && (
                    <button
                      className="btn btn-success btn-sm"
                      onClick={() => handleQuickApprove(item.id, item.ledger, item.voucher_type)}
                      title="Approve Transaction"
                    >
                      <Check size={14} /> Approve
                    </button>
                  )}
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => openEditModal(item)}
                    title="Change Ledger / Voucher"
                  >
                    <Edit2 size={14} /> {isDuplicate ? 'Override' : 'Edit'}
                  </button>
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => handleReject(item.id)}
                    title="Reject Transaction"
                  >
                    <Ban size={14} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Edit Decision Modal */}
      {editingItem && (
        <Modal
          isOpen={!!editingItem}
          onClose={() => setEditingItem(null)}
          title={`Review Transaction #${editingItem.id}`}
          footer={
            <>
              <button className="btn btn-secondary" onClick={() => setEditingItem(null)}>
                Cancel
              </button>
              <button className="btn btn-primary" onClick={handleSaveEdit}>
                Save & Approve
              </button>
            </>
          }
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '4px', fontSize: '13px' }}>
              <div><strong>Narration:</strong> {editingItem.description}</div>
              <div><strong>Amount:</strong> {formatCurrency(editingItem.amount)} ({editingItem.transaction_type})</div>
            </div>

            <div className="form-group" style={{ margin: 0 }}>
              <label className="form-label">Tally Ledger *</label>
              <select
                className="select"
                value={editLedger}
                onChange={(e) => setEditLedger(e.target.value)}
              >
                <option value="">-- Choose Tally Ledger --</option>
                {ledgers.map((l) => (
                  <option key={l.name} value={l.name}>
                    {l.name} ({l.group})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group" style={{ margin: 0 }}>
              <label className="form-label">Voucher Type *</label>
              <select
                className="select"
                value={editVoucher}
                onChange={(e) => setEditVoucher(e.target.value)}
              >
                <option value="Payment">Payment</option>
                <option value="Receipt">Receipt</option>
                <option value="Contra">Contra</option>
                <option value="Journal">Journal</option>
              </select>
            </div>
          </div>
        </Modal>
      )}

      {/* Bulk Approval Safety Modal (PRD Section 27) */}
      <Modal
        isOpen={isBulkModalOpen}
        onClose={() => setIsBulkModalOpen(false)}
        title="Confirm Safe Bulk Approval"
        footer={
          <>
            <button 
              className="btn btn-secondary" 
              onClick={() => setIsBulkModalOpen(false)}
              disabled={bulkProcessing}
            >
              Cancel
            </button>
            <button 
              className="btn btn-success" 
              onClick={handleExecuteBulkApprove}
              disabled={bulkProcessing}
            >
              {bulkProcessing ? 'Approving...' : `Confirm Approval (${approvableCount} items)`}
            </button>
          </>
        }
      >
        <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
          <div style={{ color: 'var(--primary)', flexShrink: 0 }}>
            <ShieldAlert size={24} />
          </div>
          <div>
            <h4 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '6px' }}>
              Approve {approvableCount} validated transactions?
            </h4>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: '1.4' }}>
              Only transactions that already have a resolved Tally Ledger will be approved.
              Any duplicate entries or unassigned ledgers are strictly protected and will remain in the review queue.
            </p>
          </div>
        </div>
      </Modal>
    </div>
  );
}
