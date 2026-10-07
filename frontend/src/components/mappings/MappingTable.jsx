import React from 'react';
import { Edit2, Trash2, CheckCircle2, XCircle } from 'lucide-react';
import EmptyState from '../common/EmptyState';

export default function MappingTable({ mappings, onEdit, onDelete, onToggleActive }) {
  if (!mappings || mappings.length === 0) {
    return (
      <div className="table-container">
        <EmptyState 
          title="No mapping rules configured" 
          description="Create keyword-to-ledger rules to automatically classify transactions."
        />
      </div>
    );
  }

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>Keyword / Pattern</th>
            <th>Tally Ledger</th>
            <th>Voucher Type</th>
            <th style={{ textAlign: 'center' }}>Priority</th>
            <th style={{ textAlign: 'center' }}>Status</th>
            <th style={{ textAlign: 'right' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {mappings.map((m) => (
            <tr key={m.id}>
              <td>
                <code style={{
                  background: '#f1f5f9',
                  padding: '2px 8px',
                  borderRadius: '4px',
                  fontSize: '12px',
                  fontWeight: '600',
                  color: '#0f172a'
                }}>
                  {m.keyword}
                </code>
              </td>
              <td style={{ fontWeight: '500' }}>
                {m.ledger_name}
              </td>
              <td>
                <span style={{
                  fontSize: '12px',
                  color: 'var(--text-secondary)'
                }}>
                  {m.voucher_type}
                </span>
              </td>
              <td style={{ textAlign: 'center', fontWeight: '600', color: 'var(--text-muted)' }}>
                {m.priority}
              </td>
              <td style={{ textAlign: 'center' }}>
                <span 
                  onClick={() => onToggleActive?.(m)}
                  style={{
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontSize: '12px',
                    fontWeight: '600',
                    color: m.active ? 'var(--success)' : 'var(--text-muted)'
                  }}
                >
                  {m.active ? <CheckCircle2 size={14} /> : <XCircle size={14} />}
                  {m.active ? 'Active' : 'Disabled'}
                </span>
              </td>
              <td style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                <div style={{ display: 'inline-flex', gap: '6px' }}>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => onEdit(m)}
                    title="Edit Rule"
                  >
                    <Edit2 size={13} />
                  </button>
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => onDelete(m.id)}
                    title="Delete Rule"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
