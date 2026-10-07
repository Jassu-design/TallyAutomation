import React from 'react';
import Badge from '../common/Badge';
import EmptyState from '../common/EmptyState';
import { formatCurrency, formatDate } from '../../utils/formatters';
import { Eye, Check, Send, AlertCircle, ArrowUpDown } from 'lucide-react';

export default function TransactionTable({
  transactions,
  selectedIds,
  onSelectId,
  onSelectAll,
  onRowClick,
  onQuickApprove,
  onQuickPost,
  sortBy,
  sortOrder,
  onSort
}) {
  if (!transactions || transactions.length === 0) {
    return (
      <div className="table-container">
        <EmptyState 
          title="No transactions found" 
          description="Try adjusting your search or filters, or upload a new bank statement." 
        />
      </div>
    );
  }

  const allSelected = transactions.length > 0 && transactions.every((t) => selectedIds.includes(t.id));

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th style={{ width: '40px', textAlign: 'center' }}>
              <input
                type="checkbox"
                checked={allSelected}
                onChange={(e) => onSelectAll(e.target.checked)}
              />
            </th>
            <th 
              onClick={() => onSort?.('date')}
              style={{ cursor: 'pointer' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                Date <ArrowUpDown size={12} />
              </div>
            </th>
            <th>Description / Narration</th>
            <th>Reference</th>
            <th 
              onClick={() => onSort?.('amount')}
              style={{ cursor: 'pointer', textAlign: 'right' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '4px' }}>
                Amount <ArrowUpDown size={12} />
              </div>
            </th>
            <th style={{ textAlign: 'center' }}>Type</th>
            <th>Suggested Ledger</th>
            <th>Voucher</th>
            <th>Status</th>
            <th style={{ textAlign: 'right' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((t) => {
            const isSelected = selectedIds.includes(t.id);
            const isDebit = t.transaction_type === 'DEBIT';

            return (
              <tr 
                key={t.id} 
                onClick={() => onRowClick(t.id)}
                style={{
                  cursor: 'pointer',
                  backgroundColor: isSelected ? '#eff6ff' : 'transparent'
                }}
              >
                <td 
                  style={{ textAlign: 'center' }}
                  onClick={(e) => e.stopPropagation()}
                >
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={(e) => onSelectId(t.id, e.target.checked)}
                  />
                </td>
                <td style={{ whiteSpace: 'nowrap', fontWeight: '500' }}>
                  {formatDate(t.date)}
                </td>
                <td style={{ maxWidth: '280px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  <div style={{ fontWeight: '500' }} title={t.description}>
                    {t.description}
                  </div>
                  {t.review_reason && t.status === 'REVIEW_REQUIRED' && (
                    <div style={{ fontSize: '11px', color: 'var(--warning)', marginTop: '2px' }}>
                      ⚠ {t.review_reason}
                    </div>
                  )}
                  {t.error_message && (
                    <div style={{ fontSize: '11px', color: 'var(--danger)', marginTop: '2px' }}>
                      ✖ {t.error_message}
                    </div>
                  )}
                </td>
                <td style={{ fontSize: '12px', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                  {t.reference || '—'}
                </td>
                <td style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                  <span className={isDebit ? 'amount-debit' : 'amount-credit'}>
                    {isDebit ? '-' : '+'}{formatCurrency(t.amount)}
                  </span>
                </td>
                <td style={{ textAlign: 'center' }}>
                  <span style={{
                    fontSize: '11px',
                    fontWeight: '600',
                    color: isDebit ? 'var(--danger)' : 'var(--success)',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    backgroundColor: isDebit ? 'var(--danger-bg)' : 'var(--success-bg)'
                  }}>
                    {t.transaction_type}
                  </span>
                </td>
                <td style={{ maxWidth: '180px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  <span style={{ fontWeight: t.ledger ? '500' : '400', color: t.ledger ? 'var(--text-primary)' : 'var(--text-muted)' }}>
                    {t.ledger || '— Unassigned —'}
                  </span>
                </td>
                <td>
                  <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                    {t.voucher_type || '—'}
                  </span>
                </td>
                <td>
                  <Badge status={t.status} />
                </td>
                <td style={{ textAlign: 'right', whiteSpace: 'nowrap' }} onClick={(e) => e.stopPropagation()}>
                  <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => onRowClick(t.id)}
                      title="Inspect Transaction"
                    >
                      <Eye size={13} />
                    </button>

                    {t.status === 'REVIEW_REQUIRED' && (
                      <button
                        className="btn btn-success btn-sm"
                        onClick={() => onQuickApprove(t.id)}
                        title="Approve for Posting"
                      >
                        <Check size={13} />
                      </button>
                    )}

                    {(t.status === 'APPROVED' || t.status === 'FAILED') && (
                      <button
                        className="btn btn-primary btn-sm"
                        onClick={() => onQuickPost(t.id)}
                        title="Post to TallyPrime"
                      >
                        <Send size={13} />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
