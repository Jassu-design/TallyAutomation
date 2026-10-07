import React from 'react';
import { AlertTriangle, AlertCircle, ArrowRight, HelpCircle, CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { formatCurrency } from '../../utils/formatters';

export default function AttentionPanel({ attention }) {
  const navigate = useNavigate();
  const hasItems = (attention?.review_count > 0) || (attention?.failed_count > 0) || (!attention?.is_tally_connected);

  if (!hasItems) {
    return (
      <div className="card" style={{ borderLeft: '4px solid var(--success)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            backgroundColor: 'var(--success-bg)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--success)'
          }}>
            <CheckCircle size={20} />
          </div>
          <div>
            <h4 style={{ fontSize: '14px', fontWeight: '600' }}>All clear! No items require attention</h4>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              All imported transactions have been reviewed, approved, or posted successfully.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card" style={{ borderLeft: '4px solid var(--warning)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertTriangle size={18} color="var(--warning)" />
          <h3 style={{ fontSize: '15px', fontWeight: '600' }}>Attention Required</h3>
        </div>
        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
          {attention?.review_count + attention?.failed_count} unresolved items
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {attention?.review_count > 0 && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '10px 14px',
            backgroundColor: '#fffbeb',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid #fef3c7'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <HelpCircle size={16} color="var(--warning)" />
              <div>
                <strong style={{ fontSize: '13px', color: '#92400e' }}>
                  {attention.review_count} transactions in Review Queue
                </strong>
                <p style={{ fontSize: '11px', color: '#b45309' }}>
                  {attention.missing_ledger_count} transactions need manual ledger assignment
                </p>
              </div>
            </div>
            <button 
              className="btn btn-secondary btn-sm" 
              onClick={() => navigate('/review-queue')}
            >
              Resolve <ArrowRight size={12} />
            </button>
          </div>
        )}

        {attention?.failed_count > 0 && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '10px 14px',
            backgroundColor: '#fef2f2',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid #fee2e2'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <AlertCircle size={16} color="var(--danger)" />
              <div>
                <strong style={{ fontSize: '13px', color: '#991b1b' }}>
                  {attention.failed_count} postings failed or rejected
                </strong>
                <p style={{ fontSize: '11px', color: '#b91c1c' }}>
                  Inspect errors and retry failed vouchers to TallyPrime
                </p>
              </div>
            </div>
            <button 
              className="btn btn-secondary btn-sm" 
              onClick={() => navigate('/transactions?status=FAILED')}
            >
              View Failures <ArrowRight size={12} />
            </button>
          </div>
        )}

        {!attention?.is_tally_connected && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '10px 14px',
            backgroundColor: '#fef2f2',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid #fee2e2'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <AlertCircle size={16} color="var(--danger)" />
              <span style={{ fontSize: '13px', color: '#991b1b' }}>
                TallyPrime is unreachable. Postings are currently queued.
              </span>
            </div>
            <button 
              className="btn btn-secondary btn-sm" 
              onClick={() => navigate('/tally')}
            >
              Check Tally <ArrowRight size={12} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
