import React, { useState, useEffect } from 'react';
import PageHeader from '../components/layout/PageHeader';
import LoadingState from '../components/common/LoadingState';
import Badge from '../components/common/Badge';
import { TallyAPI } from '../services/api';
import { useToast } from '../hooks/useToast';
import { formatCurrency, formatDate } from '../utils/formatters';
import { Server, CheckCircle2, AlertCircle, Send, RefreshCw } from 'lucide-react';

export default function TallyPrime() {
  const { showSuccess, showError } = useToast();
  const [tallyStatus, setTallyStatus] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [posting, setPosting] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [statusRes, historyRes] = await Promise.all([
        TallyAPI.getStatus(),
        TallyAPI.getHistory(),
      ]);
      setTallyStatus(statusRes);
      setHistory(historyRes || []);
    } catch (err) {
      showError(err.message || 'Failed to connect to Tally service.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handlePostAll = async () => {
    setPosting(true);
    try {
      const res = await TallyAPI.postBulk([]);   // backend posts all APPROVED when ids=[]
      showSuccess(`Posted ${res.success_count ?? 0} vouchers to TallyPrime.`);
      if (res.failed_count > 0) showError(`${res.failed_count} failed to post.`);
      fetchData();
    } catch (err) {
      showError(err.message || 'Bulk post failed.');
    } finally {
      setPosting(false);
    }
  };

  const isConnected = tallyStatus?.connected;
  const companyName = tallyStatus?.company || 'Pawan Glasses';

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <PageHeader
        title="Post to Tally"
        subtitle="Push approved transactions to TallyPrime as vouchers"
        actions={
          <button className="btn btn-secondary" onClick={fetchData} disabled={loading}>
            <RefreshCw size={14} className={loading ? 'spin' : ''} /> Refresh
          </button>
        }
      />

      {/* Connection Banner */}
      <div className="card" style={{
        padding: '16px 20px',
        marginBottom: '20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Server size={20} color={isConnected ? 'var(--success)' : 'var(--danger)'} />
          <div>
            <span style={{ fontWeight: '600', fontSize: '14px' }}>Company: {companyName}</span>
          </div>
          <span style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '5px',
            padding: '3px 10px',
            borderRadius: 'var(--radius-full)',
            background: isConnected ? 'var(--success-bg)' : 'var(--danger-bg)',
            color: isConnected ? 'var(--success)' : 'var(--danger)',
            fontSize: '12px',
            fontWeight: '600'
          }}>
            {isConnected ? <CheckCircle2 size={13} /> : <AlertCircle size={13} />}
            {isConnected ? 'Connected' : 'Offline'}
          </span>
        </div>

        <button
          className="btn btn-primary"
          onClick={handlePostAll}
          disabled={posting || !isConnected}
        >
          <Send size={14} />
          {posting ? 'Posting...' : 'Post All Approved to Tally'}
        </button>
      </div>

      {/* Posting History */}
      <div className="card" style={{ padding: '20px' }}>
        <h3 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '16px' }}>
          Recent Postings
        </h3>

        {loading ? (
          <LoadingState message="Loading..." />
        ) : history.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)', fontSize: '13px' }}>
            No vouchers posted yet.
          </div>
        ) : (
          <div className="table-container" style={{ border: 'none', boxShadow: 'none' }}>
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Description</th>
                  <th style={{ textAlign: 'right' }}>Amount</th>
                  <th>Voucher No</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {history.map((h) => (
                  <tr key={h.id}>
                    <td style={{ whiteSpace: 'nowrap', fontSize: '12px', color: 'var(--text-muted)' }}>
                      {h.posted_at ? formatDate(h.posted_at) : '—'}
                    </td>
                    <td style={{ maxWidth: '260px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {h.transaction?.description || `Transaction #${h.transaction_id}`}
                    </td>
                    <td style={{ textAlign: 'right', fontWeight: '600' }}>
                      {formatCurrency(h.transaction?.amount)}
                    </td>
                    <td>
                      {h.voucher_number ? (
                        <code style={{
                          background: 'var(--success-bg)',
                          color: 'var(--success)',
                          padding: '2px 7px',
                          borderRadius: '4px',
                          fontWeight: '600',
                          fontSize: '12px'
                        }}>
                          {h.voucher_number}
                        </code>
                      ) : '—'}
                    </td>
                    <td>
                      <Badge status={h.status === 'SUCCESS' ? 'POSTED' : 'FAILED'} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
