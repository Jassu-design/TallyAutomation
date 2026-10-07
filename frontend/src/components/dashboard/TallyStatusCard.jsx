import React from 'react';
import { Server, CheckCircle2, AlertCircle, RefreshCw, Zap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function TallyStatusCard({ tallyStatus, onTestConnection, isTesting }) {
  const navigate = useNavigate();
  const isConnected = tallyStatus?.connected;
  const isSimulation = tallyStatus?.mode === 'SIMULATION';

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Server size={18} color="var(--primary)" />
            <h3 style={{ fontSize: '15px', fontWeight: '600' }}>TallyPrime Gateway</h3>
          </div>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
            Local XML Server Interface
          </p>
        </div>

        <span style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          padding: '4px 10px',
          borderRadius: 'var(--radius-full)',
          background: isConnected ? 'var(--success-bg)' : 'var(--danger-bg)',
          border: `1px solid ${isConnected ? 'var(--success-border)' : 'var(--danger-border)'}`,
          color: isConnected ? 'var(--success)' : 'var(--danger)',
          fontSize: '12px',
          fontWeight: '600'
        }}>
          {isConnected ? <CheckCircle2 size={14} /> : <AlertCircle size={14} />}
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
      </div>

      <div style={{
        background: '#f8fafc',
        borderRadius: 'var(--radius-sm)',
        padding: '12px 14px',
        marginBottom: '16px',
        fontSize: '13px',
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '8px'
      }}>
        <div>
          <span style={{ color: 'var(--text-muted)', fontSize: '11px', display: 'block' }}>Target Company</span>
          <strong style={{ fontWeight: '600' }}>{tallyStatus?.company || 'ABC Pvt Ltd'}</strong>
        </div>
        <div>
          <span style={{ color: 'var(--text-muted)', fontSize: '11px', display: 'block' }}>Endpoint</span>
          <code>{tallyStatus?.host || 'localhost'}:{tallyStatus?.port || 9000}</code>
        </div>
        <div>
          <span style={{ color: 'var(--text-muted)', fontSize: '11px', display: 'block' }}>Mode</span>
          <span style={{
            color: isSimulation ? '#4338ca' : '#047857',
            fontWeight: '600',
            fontSize: '12px'
          }}>
            {isSimulation ? '⚡ Simulation Active' : '● Live Tally Connection'}
          </span>
        </div>
        <div>
          <span style={{ color: 'var(--text-muted)', fontSize: '11px', display: 'block' }}>Latency</span>
          <span>{tallyStatus?.latency_ms ? `${tallyStatus.latency_ms} ms` : '—'}</span>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '8px' }}>
        <button 
          className="btn btn-secondary btn-sm" 
          onClick={onTestConnection}
          disabled={isTesting}
          style={{ flex: 1, justifyContent: 'center' }}
        >
          <RefreshCw size={14} className={isTesting ? 'spin' : ''} />
          {isTesting ? 'Checking...' : 'Test Connection'}
        </button>
        <button 
          className="btn btn-secondary btn-sm" 
          onClick={() => navigate('/tally')}
          style={{ justifyContent: 'center' }}
        >
          Manage
        </button>
      </div>
    </div>
  );
}
