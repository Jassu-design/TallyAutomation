import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import PageHeader from '../components/layout/PageHeader';
import LoadingState from '../components/common/LoadingState';
import { TransactionAPI, TallyAPI } from '../services/api';
import { useToast } from '../hooks/useToast';
import { formatCurrency, formatDate } from '../utils/formatters';
import { Send, Check, ChevronLeft, ChevronRight } from 'lucide-react';

const STATUS_COLORS = {
  APPROVED:       { bg: '#eff6ff', color: '#2563eb' },
  REVIEW_REQUIRED:{ bg: '#fef3c7', color: '#d97706' },
  POSTED:         { bg: 'var(--success-bg)', color: 'var(--success)' },
  FAILED:         { bg: 'var(--danger-bg)', color: 'var(--danger)' },
};

function StatusBadge({ status }) {
  const s = STATUS_COLORS[status] || { bg: '#f1f5f9', color: '#64748b' };
  return (
    <span style={{
      display: 'inline-block',
      padding: '2px 8px',
      borderRadius: 'var(--radius-full)',
      fontSize: '11px',
      fontWeight: '600',
      background: s.bg,
      color: s.color,
    }}>
      {status?.replace('_', ' ')}
    </span>
  );
}

export default function Transactions() {
  const { showSuccess, showError, showWarning } = useToast();
  const navigate = useNavigate();

  const [transactions, setTransactions] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const pageSize = 25;
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [ledgers, setLedgers] = useState([]);

  // inline approve state: { [id]: { ledger, voucherType } }
  const [approveDraft, setApproveDraft] = useState({});
  const [actionLoading, setActionLoading] = useState({});
  const [bulkPosting, setBulkPosting] = useState(false);

  const fetchTransactions = useCallback(async () => {
    try {
      setLoading(true);
      const params = { page, page_size: pageSize };
      if (statusFilter !== 'ALL') params.status = statusFilter;
      const res = await TransactionAPI.getTransactions(params);
      setTransactions(res.items || []);
      setTotal(res.total || 0);
      setTotalPages(res.total_pages || 1);
    } catch (err) {
      showError(err.message || 'Failed to fetch transactions.');
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, statusFilter, showError]);

  useEffect(() => { fetchTransactions(); }, [fetchTransactions]);

  useEffect(() => {
    TallyAPI.getLedgers()
      .then((list) => setLedgers(list || []))
      .catch(() => {});
  }, []);

  const setAction = (id, val) => setActionLoading((p) => ({ ...p, [id]: val }));

  const handleApprove = async (id) => {
    const draft = approveDraft[id] || {};
    if (!draft.ledger) { showError('Please select a ledger first.'); return; }
    setAction(id, true);
    try {
      await TransactionAPI.approveTransaction(id, {
        ledger: draft.ledger,
        voucher_type: draft.voucherType || 'Payment',
      });
      showSuccess(`Transaction #${id} approved.`);
      fetchTransactions();
    } catch (err) {
      showError(err.message || 'Approval failed.');
    } finally {
      setAction(id, false);
    }
  };

  const handlePost = async (id) => {
    setAction(id, true);
    try {
      const res = await TallyAPI.postTransaction(id);
      if (res.success) {
        showSuccess(`Posted! Voucher: ${res.voucher_number}`);
      } else {
        showError(`Post failed: ${res.error}`);
      }
      fetchTransactions();
    } catch (err) {
      showError(err.message || 'Failed to post voucher.');
    } finally {
      setAction(id, false);
    }
  };

  const handleApproveAndPostAll = async () => {
    setBulkPosting(true);
    try {
      const reviewIds = transactions
        .filter((t) => t.status === 'REVIEW_REQUIRED' && t.ledger)
        .map((t) => t.id);
      if (reviewIds.length > 0) {
        const approveRes = await TransactionAPI.bulkApprove(reviewIds);
        if (approveRes.skipped?.length > 0) {
          showWarning(`${approveRes.skipped.length} skipped (missing ledger).`);
        }
      }
      const postRes = await TallyAPI.postBulk([]);
      showSuccess(`Posted ${postRes.success_count ?? 0} vouchers.`);
      if (postRes.failed_count > 0) showError(`${postRes.failed_count} failed.`);
      fetchTransactions();
    } catch (err) {
      showError(err.message || 'Bulk action failed.');
    } finally {
      setBulkPosting(false);
    }
  };

  return (
    <div>
      <PageHeader
        title="Transactions"
        subtitle={`${total} bank transactions`}
        actions={
          <button
            className="btn btn-primary"
            onClick={handleApproveAndPostAll}
            disabled={bulkPosting}
          >
            <Check size={14} />
            {bulkPosting ? 'Processing...' : 'Approve All & Post All'}
          </button>
        }
      />

      {/* Simple Status Filter */}
      <div style={{ marginBottom: '16px', display: 'flex', gap: '8px', alignItems: 'center' }}>
        <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Filter:</span>
        {['ALL', 'REVIEW_REQUIRED', 'APPROVED', 'POSTED'].map((s) => (
          <button
            key={s}
            className={`btn btn-sm ${statusFilter === s ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => { setStatusFilter(s); setPage(1); }}
          >
            {s === 'ALL' ? 'All' : s.replace('_', ' ')}
          </button>
        ))}
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <LoadingState message="Loading transactions..." />
        ) : transactions.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)', fontSize: '13px' }}>
            No transactions found.{' '}
            <button className="btn btn-secondary btn-sm" onClick={() => navigate('/upload')}>
              Upload a statement
            </button>
          </div>
        ) : (
          <div className="table-container" style={{ border: 'none', boxShadow: 'none' }}>
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Description</th>
                  <th style={{ textAlign: 'right' }}>Amount</th>
                  <th>Ledger</th>
                  <th>Voucher</th>
                  <th>Status</th>
                  <th style={{ textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((txn) => (
                  <tr key={txn.id}>
                    <td style={{ whiteSpace: 'nowrap', fontSize: '12px', color: 'var(--text-muted)' }}>
                      {formatDate(txn.date)}
                    </td>
                    <td style={{ maxWidth: '240px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {txn.description}
                    </td>
                    <td style={{ textAlign: 'right', fontWeight: '600' }}>
                      {formatCurrency(txn.amount)}
                    </td>
                    <td style={{ fontSize: '12px' }}>{txn.ledger || <span style={{ color: 'var(--text-muted)' }}>—</span>}</td>
                    <td style={{ fontSize: '12px' }}>
                      {txn.status === 'POSTED' && txn.voucher_number ? (
                        <code style={{
                          background: 'var(--success-bg)',
                          color: 'var(--success)',
                          padding: '2px 7px',
                          borderRadius: '4px',
                          fontWeight: '600',
                          fontSize: '11px'
                        }}>
                          {txn.voucher_number}
                        </code>
                      ) : <span style={{ color: 'var(--text-muted)' }}>—</span>}
                    </td>
                    <td><StatusBadge status={txn.status} /></td>
                    <td style={{ textAlign: 'right' }}>
                      {txn.status === 'APPROVED' && (
                        <button
                          className="btn btn-primary btn-sm"
                          onClick={() => handlePost(txn.id)}
                          disabled={actionLoading[txn.id]}
                        >
                          <Send size={12} /> Post to Tally
                        </button>
                      )}
                      {txn.status === 'REVIEW_REQUIRED' && (
                        <div style={{ display: 'flex', gap: '6px', justifyContent: 'flex-end', alignItems: 'center' }}>
                          <select
                            style={{
                              fontSize: '12px',
                              padding: '4px 6px',
                              border: '1px solid var(--border-color)',
                              borderRadius: 'var(--radius-sm)',
                              background: 'white',
                              maxWidth: '150px'
                            }}
                            value={approveDraft[txn.id]?.ledger || ''}
                            onChange={(e) =>
                              setApproveDraft((p) => ({
                                ...p,
                                [txn.id]: { ...(p[txn.id] || {}), ledger: e.target.value }
                              }))
                            }
                          >
                            <option value="">Select Ledger</option>
                            {ledgers.map((l) => (
                              <option key={l.name || l} value={l.name || l}>{l.name || l}</option>
                            ))}
                          </select>
                          <button
                            className="btn btn-secondary btn-sm"
                            onClick={() => handleApprove(txn.id)}
                            disabled={actionLoading[txn.id]}
                          >
                            <Check size={12} /> Approve
                          </button>
                        </div>
                      )}
                      {txn.status === 'POSTED' && (
                        <span style={{ fontSize: '11px', color: 'var(--success)', fontWeight: '600' }}>✓ Done</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginTop: '16px',
          fontSize: '13px',
          color: 'var(--text-muted)'
        }}>
          <span>
            Showing {total > 0 ? (page - 1) * pageSize + 1 : 0}–{Math.min(page * pageSize, total)} of {total}
          </span>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <button className="btn btn-secondary btn-sm" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page <= 1}>
              <ChevronLeft size={14} /> Prev
            </button>
            <span>Page {page} of {totalPages}</span>
            <button className="btn btn-secondary btn-sm" onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page >= totalPages}>
              Next <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
