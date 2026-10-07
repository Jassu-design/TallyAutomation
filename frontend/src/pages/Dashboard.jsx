import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import PageHeader from '../components/layout/PageHeader';
import StatCard from '../components/dashboard/StatCard';
import TallyStatusCard from '../components/dashboard/TallyStatusCard';
import AttentionPanel from '../components/dashboard/AttentionPanel';
import LoadingState from '../components/common/LoadingState';
import Badge from '../components/common/Badge';
import { DashboardAPI, TallyAPI } from '../services/api';
import { useToast } from '../hooks/useToast';
import { 
  FileSpreadsheet, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Copy, 
  Upload, 
  ArrowRight,
  TrendingUp,
  History
} from 'lucide-react';

export default function Dashboard() {
  const navigate = useNavigate();
  const { showSuccess, showError } = useToast();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isTestingTally, setIsTestingTally] = useState(false);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const res = await DashboardAPI.getSummary();
      setData(res);
    } catch (err) {
      showError('Failed to load dashboard metrics: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTestTally = async () => {
    setIsTestingTally(true);
    try {
      const res = await TallyAPI.testConnection();
      setData((prev) => ({ ...prev, tally_status: res }));
      if (res.connected) {
        showSuccess(res.message);
      } else {
        showError(res.message);
      }
    } catch (err) {
      showError('Tally connection test error: ' + err.message);
    } finally {
      setIsTestingTally(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (loading && !data) {
    return <LoadingState message="Loading dashboard metrics..." />;
  }

  const metrics = data?.metrics || {};

  return (
    <div>
      <PageHeader
        title="Accounting Dashboard"
        subtitle="Real-time bank statement ingestion and TallyPrime posting overview"
        actions={
          <button 
            className="btn btn-primary"
            onClick={() => navigate('/imports/upload')}
          >
            <Upload size={16} />
            Upload Statement
          </button>
        }
      />

      {/* Summary Stat Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
        marginBottom: '24px'
      }}>
        <StatCard
          title="Total Processed"
          value={metrics.total}
          subtitle="Transactions extracted"
          icon={FileSpreadsheet}
          color="var(--primary)"
          onClick={() => navigate('/transactions')}
        />
        <StatCard
          title="Posted to Tally"
          value={metrics.posted}
          subtitle="Vouchers created"
          icon={CheckCircle2}
          color="var(--success)"
          onClick={() => navigate('/transactions?status=POSTED')}
        />
        <StatCard
          title="Review Queue"
          value={metrics.review}
          subtitle="Require user decision"
          icon={AlertTriangle}
          color="var(--warning)"
          onClick={() => navigate('/review-queue')}
        />
        <StatCard
          title="Duplicates Blocked"
          value={metrics.duplicate}
          subtitle="Prevented double entry"
          icon={Copy}
          color="var(--duplicate)"
          onClick={() => navigate('/transactions?status=DUPLICATE')}
        />
        <StatCard
          title="Failed / Invalid"
          value={metrics.failed}
          subtitle="Errors requiring action"
          icon={XCircle}
          color="var(--danger)"
          onClick={() => navigate('/transactions?status=FAILED')}
        />
      </div>

      {/* Two Column Grid: Tally Status & Attention Panel */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '20px',
        marginBottom: '24px'
      }}>
        <TallyStatusCard
          tallyStatus={data?.tally_status}
          onTestConnection={handleTestTally}
          isTesting={isTestingTally}
        />
        <AttentionPanel attention={data?.attention} />
      </div>

      {/* Recent Imports */}
      <div className="card" style={{ padding: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '15px', fontWeight: '600' }}>Recent Statement Batches</h3>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Latest uploaded bank statements</p>
          </div>
          <button 
            className="btn btn-secondary btn-sm"
            onClick={() => navigate('/imports')}
          >
            View All Imports <ArrowRight size={13} />
          </button>
        </div>

        {(!data?.recent_imports || data.recent_imports.length === 0) ? (
          <div style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)' }}>
            No statements uploaded yet. Click "Upload Statement" to begin.
          </div>
        ) : (
          <div className="table-container" style={{ border: 'none', boxShadow: 'none' }}>
            <table>
              <thead>
                <tr>
                  <th>File Name</th>
                  <th>Bank</th>
                  <th>Date</th>
                  <th style={{ textAlign: 'right' }}>Transactions</th>
                  <th style={{ textAlign: 'right' }}>Posted</th>
                  <th style={{ textAlign: 'right' }}>Review</th>
                  <th>Status</th>
                  <th style={{ textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {data.recent_imports.map((batch) => (
                  <tr key={batch.id}>
                    <td style={{ fontWeight: '500' }}>{batch.filename}</td>
                    <td>{batch.bank_name}</td>
                    <td style={{ color: 'var(--text-muted)' }}>{batch.date}</td>
                    <td style={{ textAlign: 'right', fontWeight: '600' }}>{batch.transactions}</td>
                    <td style={{ textAlign: 'right', color: 'var(--success)', fontWeight: '600' }}>{batch.posted}</td>
                    <td style={{ textAlign: 'right', color: 'var(--warning)', fontWeight: '600' }}>{batch.review}</td>
                    <td>
                      <Badge status={batch.status} />
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button 
                        className="btn btn-secondary btn-sm"
                        onClick={() => navigate(`/imports/${batch.id}`)}
                      >
                        Details
                      </button>
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
