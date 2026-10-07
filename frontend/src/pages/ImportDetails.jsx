import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import PageHeader from '../components/layout/PageHeader';
import LoadingState from '../components/common/LoadingState';
import Badge from '../components/common/Badge';
import { BankAPI } from '../services/api';
import { useToast } from '../hooks/useToast';
import { formatCurrency, formatDate } from '../utils/formatters';
import { ArrowLeft, CheckCircle2, AlertTriangle, FileSpreadsheet, Send, ArrowRight } from 'lucide-react';

export default function ImportDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { showError } = useToast();
  const [batch, setBatch] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBatch = async () => {
      try {
        setLoading(true);
        const res = await BankAPI.getImportDetails(id);
        setBatch(res);
      } catch (err) {
        showError(err.message || 'Failed to load import details.');
      } finally {
        setLoading(false);
      }
    };
    fetchBatch();
  }, [id]);

  if (loading) return <LoadingState message="Loading import batch details..." />;
  if (!batch) return <div>Batch not found.</div>;

  const steps = [
    { name: 'Uploaded', time: batch.uploaded_at, done: true },
    { name: 'Extracted', desc: `${batch.total_transactions} items found`, done: true },
    { name: 'Validated', desc: `${batch.total_transactions - batch.failed_transactions} valid`, done: true },
    { name: 'Mapped', desc: `${batch.total_transactions - batch.review_transactions} mapped`, done: true },
    { name: 'Ready / Posted', desc: `${batch.posted_transactions} posted to Tally`, done: batch.posted_transactions > 0 },
  ];

  return (
    <div>
      <PageHeader
        title={`Import Batch #${batch.id}`}
        subtitle={`${batch.filename} (${batch.bank_name})`}
        actions={
          <div style={{ display: 'flex', gap: '8px' }}>
            <button className="btn btn-secondary btn-sm" onClick={() => navigate('/imports')}>
              <ArrowLeft size={14} /> Back to Imports
            </button>
            <button 
              className="btn btn-primary btn-sm"
              onClick={() => navigate(`/transactions?import_id=${batch.id}`)}
            >
              View All Transactions <ArrowRight size={14} />
            </button>
          </div>
        }
      />

      {/* Batch Overview Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '12px',
        marginBottom: '20px'
      }}>
        <div className="card" style={{ padding: '16px' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Transactions</span>
          <strong style={{ fontSize: '20px', display: 'block', marginTop: '4px' }}>{batch.total_transactions}</strong>
        </div>
        <div className="card" style={{ padding: '16px' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Processed</span>
          <strong style={{ fontSize: '20px', display: 'block', marginTop: '4px' }}>{batch.processed_transactions}</strong>
        </div>
        <div className="card" style={{ padding: '16px', borderLeft: '4px solid var(--warning)' }}>
          <span style={{ fontSize: '11px', color: 'var(--warning)', textTransform: 'uppercase' }}>Review Required</span>
          <strong style={{ fontSize: '20px', color: 'var(--warning)', display: 'block', marginTop: '4px' }}>{batch.review_transactions}</strong>
        </div>
        <div className="card" style={{ padding: '16px', borderLeft: '4px solid var(--duplicate)' }}>
          <span style={{ fontSize: '11px', color: 'var(--duplicate)', textTransform: 'uppercase' }}>Duplicates Blocked</span>
          <strong style={{ fontSize: '20px', color: 'var(--duplicate)', display: 'block', marginTop: '4px' }}>{batch.duplicate_transactions}</strong>
        </div>
        <div className="card" style={{ padding: '16px', borderLeft: '4px solid var(--success)' }}>
          <span style={{ fontSize: '11px', color: 'var(--success)', textTransform: 'uppercase' }}>Posted to Tally</span>
          <strong style={{ fontSize: '20px', color: 'var(--success)', display: 'block', marginTop: '4px' }}>{batch.posted_transactions}</strong>
        </div>
      </div>

      {/* Processing Timeline */}
      <div className="card" style={{ padding: '20px', marginBottom: '24px' }}>
        <h3 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '16px', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
          Batch Processing Lifecycle
        </h3>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'relative' }}>
          {steps.map((st, i) => (
            <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', zIndex: 1 }}>
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                backgroundColor: st.done ? 'var(--success-bg)' : '#f1f5f9',
                border: `2px solid ${st.done ? 'var(--success)' : '#cbd5e1'}`,
                color: st.done ? 'var(--success)' : '#64748b',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: '700',
                fontSize: '12px',
                marginBottom: '6px'
              }}>
                {st.done ? '✓' : i + 1}
              </div>
              <strong style={{ fontSize: '12px' }}>{st.name}</strong>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{st.desc || st.time}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Preview Table */}
      <div className="card" style={{ padding: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <h3 style={{ fontSize: '15px', fontWeight: '600' }}>Transactions in Batch</h3>
          {batch.review_transactions > 0 && (
            <button 
              className="btn btn-secondary btn-sm"
              onClick={() => navigate('/review-queue')}
            >
              Resolve Review Queue ({batch.review_transactions})
            </button>
          )}
        </div>

        <div className="table-container" style={{ border: 'none', boxShadow: 'none' }}>
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Narration</th>
                <th>Reference</th>
                <th style={{ textAlign: 'right' }}>Amount</th>
                <th style={{ textAlign: 'center' }}>Type</th>
                <th>Suggested Ledger</th>
                <th>Voucher</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {(batch.transactions_preview || []).map((t) => (
                <tr key={t.id}>
                  <td style={{ whiteSpace: 'nowrap' }}>{formatDate(t.date)}</td>
                  <td style={{ maxWidth: '240px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {t.description}
                  </td>
                  <td>{t.reference || '—'}</td>
                  <td style={{ textAlign: 'right', fontWeight: '600' }}>
                    {formatCurrency(t.amount)}
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <span style={{
                      fontSize: '11px',
                      fontWeight: '600',
                      color: t.transaction_type === 'DEBIT' ? 'var(--danger)' : 'var(--success)'
                    }}>
                      {t.transaction_type}
                    </span>
                  </td>
                  <td>{t.ledger || '— Unassigned —'}</td>
                  <td>{t.voucher_type || '—'}</td>
                  <td>
                    <Badge status={t.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
