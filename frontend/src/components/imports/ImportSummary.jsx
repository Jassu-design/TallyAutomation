import React from 'react';
import { CheckCircle2, AlertTriangle, Copy, XCircle, ArrowRight, Upload } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function ImportSummary({ summary, onReset }) {
  const navigate = useNavigate();
  if (!summary) return null;

  const { total_transactions, valid_transactions, review_required, duplicates, failed } = summary.summary || {};

  return (
    <div className="card" style={{ padding: '32px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
        <div style={{
          width: '40px',
          height: '40px',
          borderRadius: '50%',
          backgroundColor: 'var(--success-bg)',
          color: 'var(--success)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <CheckCircle2 size={24} />
        </div>
        <div>
          <h3 style={{ fontSize: '18px', fontWeight: '600' }}>Import Summary</h3>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
            Statement: <strong>{summary.filename}</strong> ({summary.bank_name})
          </p>
        </div>
      </div>

      {/* Breakdown Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
        gap: '12px',
        marginBottom: '28px'
      }}>
        <div style={{ background: '#f8fafc', padding: '16px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'block' }}>Total Found</span>
          <strong style={{ fontSize: '22px', fontWeight: '700' }}>{total_transactions || 0}</strong>
        </div>

        <div style={{ background: 'var(--success-bg)', padding: '16px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--success-border)' }}>
          <span style={{ fontSize: '12px', color: 'var(--success)', display: 'block' }}>Valid / Approved</span>
          <strong style={{ fontSize: '22px', fontWeight: '700', color: 'var(--success)' }}>{valid_transactions || 0}</strong>
        </div>

        <div style={{ background: 'var(--warning-bg)', padding: '16px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--warning-border)' }}>
          <span style={{ fontSize: '12px', color: 'var(--warning)', display: 'block' }}>Require Review</span>
          <strong style={{ fontSize: '22px', fontWeight: '700', color: 'var(--warning)' }}>{review_required || 0}</strong>
        </div>

        <div style={{ background: 'var(--duplicate-bg)', padding: '16px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--duplicate-border)' }}>
          <span style={{ fontSize: '12px', color: 'var(--duplicate)', display: 'block' }}>Duplicates Blocked</span>
          <strong style={{ fontSize: '22px', fontWeight: '700', color: 'var(--duplicate)' }}>{duplicates || 0}</strong>
        </div>

        <div style={{ background: 'var(--danger-bg)', padding: '16px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--danger-border)' }}>
          <span style={{ fontSize: '12px', color: 'var(--danger)', display: 'block' }}>Failed / Invalid</span>
          <strong style={{ fontSize: '22px', fontWeight: '700', color: 'var(--danger)' }}>{failed || 0}</strong>
        </div>
      </div>

      {/* Action Buttons */}
      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
        <button
          className="btn btn-primary"
          onClick={() => navigate(`/transactions?import_id=${summary.batch_id}`)}
        >
          View Transactions <ArrowRight size={14} />
        </button>

        {review_required > 0 && (
          <button
            className="btn btn-secondary"
            onClick={() => navigate('/review-queue')}
          >
            Go to Review Queue ({review_required})
          </button>
        )}

        <button
          className="btn btn-secondary"
          onClick={onReset}
        >
          <Upload size={14} /> Upload Another Statement
        </button>
      </div>
    </div>
  );
}
