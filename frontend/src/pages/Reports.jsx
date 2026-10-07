import React, { useState, useEffect } from 'react';
import PageHeader from '../components/layout/PageHeader';
import LoadingState from '../components/common/LoadingState';
import { ReportsAPI } from '../services/api';
import { useToast } from '../hooks/useToast';
import { formatCurrency } from '../utils/formatters';
import { Download, PieChart, TrendingDown, TrendingUp, DollarSign, BarChart2 } from 'lucide-react';

export default function Reports() {
  const { showError, showSuccess } = useToast();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        setLoading(true);
        const res = await ReportsAPI.getSummary();
        setData(res);
      } catch (err) {
        showError(err.message || 'Failed to load report metrics.');
      } finally {
        setLoading(false);
      }
    };
    fetchReports();
  }, []);

  const handleExportCsv = () => {
    window.open(ReportsAPI.getExportUrl(), '_blank');
    showSuccess('Transaction data export initiated.');
  };

  if (loading) return <LoadingState message="Generating reports..." />;

  const fin = data?.financial_summary || {};
  const statuses = data?.status_distribution || {};
  const vouchers = data?.voucher_distribution || {};
  const banks = data?.bank_distribution || {};

  return (
    <div>
      <PageHeader
        title="Processing & Audit Reports"
        subtitle="Operational metrics, data distribution, and transaction audit exports"
        actions={
          <button className="btn btn-primary" onClick={handleExportCsv}>
            <Download size={16} /> Export to CSV
          </button>
        }
      />

      {/* Financial Flow Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '16px',
        marginBottom: '24px'
      }}>
        <div className="card" style={{ borderLeft: '4px solid var(--danger)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)', fontSize: '12px', textTransform: 'uppercase' }}>
            <TrendingDown size={16} color="var(--danger)" /> Total Debits (Outflows)
          </div>
          <div style={{ fontSize: '24px', fontWeight: '700', color: 'var(--danger)', marginTop: '6px' }}>
            {formatCurrency(fin.total_debit)}
          </div>
        </div>

        <div className="card" style={{ borderLeft: '4px solid var(--success)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)', fontSize: '12px', textTransform: 'uppercase' }}>
            <TrendingUp size={16} color="var(--success)" /> Total Credits (Inflows)
          </div>
          <div style={{ fontSize: '24px', fontWeight: '700', color: 'var(--success)', marginTop: '6px' }}>
            {formatCurrency(fin.total_credit)}
          </div>
        </div>

        <div className="card" style={{ borderLeft: '4px solid var(--primary)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)', fontSize: '12px', textTransform: 'uppercase' }}>
            <DollarSign size={16} color="var(--primary)" /> Net Statement Flow
          </div>
          <div style={{ fontSize: '24px', fontWeight: '700', color: fin.net_flow >= 0 ? 'var(--success)' : 'var(--danger)', marginTop: '6px' }}>
            {formatCurrency(fin.net_flow)}
          </div>
        </div>
      </div>

      {/* Breakdowns Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '20px',
        marginBottom: '24px'
      }}>
        {/* Status Distribution */}
        <div className="card" style={{ padding: '20px' }}>
          <h3 style={{ fontSize: '15px', fontWeight: '600', marginBottom: '16px' }}>
            Transaction Status Distribution
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {Object.keys(statuses).length === 0 ? (
              <span style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No transactions recorded yet.</span>
            ) : (
              Object.entries(statuses).map(([st, cnt]) => (
                <div key={st} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', background: '#f8fafc', borderRadius: '4px', fontSize: '13px' }}>
                  <span style={{ fontWeight: '500' }}>{st}</span>
                  <strong style={{ fontSize: '14px' }}>{cnt}</strong>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Voucher Distribution */}
        <div className="card" style={{ padding: '20px' }}>
          <h3 style={{ fontSize: '15px', fontWeight: '600', marginBottom: '16px' }}>
            Voucher Type Classification
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {Object.keys(vouchers).length === 0 ? (
              <span style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No voucher classifications yet.</span>
            ) : (
              Object.entries(vouchers).map(([vch, cnt]) => (
                <div key={vch} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', background: '#f8fafc', borderRadius: '4px', fontSize: '13px' }}>
                  <span style={{ fontWeight: '500' }}>{vch}</span>
                  <strong style={{ fontSize: '14px' }}>{cnt}</strong>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
