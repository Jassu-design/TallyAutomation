import React from 'react';
import { Search, RotateCcw, Filter } from 'lucide-react';

export default function TransactionFilters({ filters, onChange, onReset }) {
  return (
    <div className="card" style={{ padding: '16px', marginBottom: '16px' }}>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '12px',
        alignItems: 'end'
      }}>
        {/* Search */}
        <div className="form-group" style={{ margin: 0, gridColumn: 'span 2' }}>
          <label className="form-label">Search</label>
          <div style={{ position: 'relative' }}>
            <Search size={14} color="var(--text-muted)" style={{ position: 'absolute', left: '10px', top: '11px' }} />
            <input
              type="text"
              placeholder="Description, reference, ledger..."
              className="input"
              style={{ width: '100%', paddingLeft: '32px' }}
              value={filters.search || ''}
              onChange={(e) => onChange('search', e.target.value)}
            />
          </div>
        </div>

        {/* Status */}
        <div className="form-group" style={{ margin: 0 }}>
          <label className="form-label">Status</label>
          <select
            className="select"
            value={filters.status || 'ALL'}
            onChange={(e) => onChange('status', e.target.value)}
          >
            <option value="ALL">All Statuses</option>
            <option value="REVIEW_REQUIRED">Review Required</option>
            <option value="APPROVED">Approved</option>
            <option value="POSTED">Posted</option>
            <option value="FAILED">Failed</option>
            <option value="DUPLICATE">Duplicate</option>
            <option value="REJECTED">Rejected</option>
          </select>
        </div>

        {/* Type */}
        <div className="form-group" style={{ margin: 0 }}>
          <label className="form-label">Transaction Type</label>
          <select
            className="select"
            value={filters.transaction_type || 'ALL'}
            onChange={(e) => onChange('transaction_type', e.target.value)}
          >
            <option value="ALL">All Types</option>
            <option value="DEBIT">Debit (Withdrawal)</option>
            <option value="CREDIT">Credit (Deposit)</option>
          </select>
        </div>

        {/* Voucher Type */}
        <div className="form-group" style={{ margin: 0 }}>
          <label className="form-label">Voucher</label>
          <select
            className="select"
            value={filters.voucher_type || 'ALL'}
            onChange={(e) => onChange('voucher_type', e.target.value)}
          >
            <option value="ALL">All Vouchers</option>
            <option value="Payment">Payment</option>
            <option value="Receipt">Receipt</option>
            <option value="Contra">Contra</option>
            <option value="Journal">Journal</option>
          </select>
        </div>

        {/* Date From */}
        <div className="form-group" style={{ margin: 0 }}>
          <label className="form-label">Date From</label>
          <input
            type="date"
            className="input"
            value={filters.date_from || ''}
            onChange={(e) => onChange('date_from', e.target.value)}
          />
        </div>

        {/* Date To */}
        <div className="form-group" style={{ margin: 0 }}>
          <label className="form-label">Date To</label>
          <input
            type="date"
            className="input"
            value={filters.date_to || ''}
            onChange={(e) => onChange('date_to', e.target.value)}
          />
        </div>

        {/* Reset button */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <button 
            className="btn btn-secondary" 
            onClick={onReset}
            style={{ width: '100%', height: '36px', justifyContent: 'center' }}
          >
            <RotateCcw size={14} />
            Reset
          </button>
        </div>
      </div>
    </div>
  );
}
