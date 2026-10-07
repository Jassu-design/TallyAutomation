import React from 'react';
import { Loader2 } from 'lucide-react';

export default function LoadingState({ message = "Loading data..." }) {
  return (
    <div style={{
      padding: '48px 24px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '12px',
      color: 'var(--text-muted)'
    }}>
      <Loader2 size={24} className="spin" color="var(--primary)" />
      <span style={{ fontSize: '13px' }}>{message}</span>
      <style>{`
        .spin {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
