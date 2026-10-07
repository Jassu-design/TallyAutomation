import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Server, CheckCircle2, AlertCircle, RefreshCw, User } from 'lucide-react';

export default function Topbar({ tallyStatus, onRefreshStatus, isTesting }) {
  const navigate = useNavigate();
  const isConnected = tallyStatus?.connected;
  const isSimulation = tallyStatus?.mode === 'SIMULATION';

  return (
    <header style={{
      height: '60px',
      backgroundColor: 'var(--bg-surface)',
      borderBottom: '1px solid var(--border-color)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 24px',
      flexShrink: 0
    }}>
      {/* Search Bar */}
      <div style={{ display: 'flex', alignItems: 'center', width: '360px', position: 'relative' }}>
        <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px' }} />
        <input
          type="text"
          placeholder="Search transactions, ref numbers, ledgers..."
          onKeyDown={(e) => {
            if (e.key === 'Enter' && e.target.value.trim()) {
              navigate(`/transactions?search=${encodeURIComponent(e.target.value.trim())}`);
            }
          }}
          className="input"
          style={{ width: '100%', paddingLeft: '36px', height: '36px', borderRadius: 'var(--radius-sm)' }}
        />
      </div>

      {/* Right Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Tally Status Pill */}
        <div 
          onClick={() => navigate('/tally')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 12px',
            borderRadius: 'var(--radius-full)',
            background: isConnected ? 'var(--success-bg)' : 'var(--danger-bg)',
            border: `1px solid ${isConnected ? 'var(--success-border)' : 'var(--danger-border)'}`,
            fontSize: '12px',
            fontWeight: '500',
            cursor: 'pointer'
          }}
          title="Click to view TallyPrime connection details"
        >
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: isConnected ? 'var(--success)' : 'var(--danger)',
            display: 'inline-block'
          }} />
          <span style={{ color: isConnected ? 'var(--success)' : 'var(--danger)' }}>
            {isConnected ? `Tally: ${tallyStatus?.company || 'Connected'}` : 'Tally: Disconnected'}
          </span>
          {isSimulation && (
            <span style={{
              fontSize: '10px',
              background: '#e0e7ff',
              color: '#3730a3',
              padding: '1px 5px',
              borderRadius: '4px',
              fontWeight: '600'
            }}>
              SIM
            </span>
          )}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onRefreshStatus?.();
            }}
            style={{
              background: 'none',
              border: 'none',
              padding: 0,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              color: 'var(--text-muted)'
            }}
            title="Refresh status"
          >
            <RefreshCw size={12} className={isTesting ? 'spin' : ''} />
          </button>
        </div>

        {/* User Profile */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          borderLeft: '1px solid var(--border-color)',
          paddingLeft: '16px',
          fontSize: '13px'
        }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            backgroundColor: '#f1f5f9',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-secondary)'
          }}>
            <User size={16} />
          </div>
          <div>
            <div style={{ fontWeight: '500', lineHeight: '1.2' }}>Operations User</div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Accountant</div>
          </div>
        </div>
      </div>
    </header>
  );
}
