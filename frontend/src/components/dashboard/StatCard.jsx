import React from 'react';

export default function StatCard({ title, value, subtitle, icon: Icon, color = 'var(--primary)', onClick }) {
  return (
    <div 
      className="card" 
      onClick={onClick}
      style={{
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        cursor: onClick ? 'pointer' : 'default',
        borderLeft: `4px solid ${color}`,
        transition: 'transform 0.15s, box-shadow 0.15s'
      }}
      onMouseEnter={(e) => {
        if (onClick) {
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow = 'var(--shadow-md)';
        }
      }}
      onMouseLeave={(e) => {
        if (onClick) {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = 'var(--shadow-sm)';
        }
      }}
    >
      <div>
        <div style={{ fontSize: '12px', fontWeight: '500', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          {title}
        </div>
        <div style={{ fontSize: '26px', fontWeight: '700', color: 'var(--text-primary)', marginTop: '4px', lineHeight: '1.2' }}>
          {value !== undefined ? value.toLocaleString() : '0'}
        </div>
        {subtitle && (
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
            {subtitle}
          </div>
        )}
      </div>
      {Icon && (
        <div style={{
          padding: '10px',
          borderRadius: '8px',
          backgroundColor: '#f8fafc',
          color: color
        }}>
          <Icon size={20} />
        </div>
      )}
    </div>
  );
}
