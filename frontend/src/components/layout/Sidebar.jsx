import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { UploadCloud, ListFilter, Server, GitFork, Building2 } from 'lucide-react';
import { TallyAPI } from '../../services/api';

const navItems = [
  { name: 'Upload', path: '/upload', icon: UploadCloud },
  { name: 'Transactions', path: '/transactions', icon: ListFilter },
  { name: 'Post to Tally', path: '/tally', icon: Server },
  { name: 'Ledger Rules', path: '/mappings', icon: GitFork },
];

export default function Sidebar() {
  const [companyName, setCompanyName] = useState('Pawan Glasses');

  useEffect(() => {
    TallyAPI.getStatus()
      .then((res) => { if (res?.company) setCompanyName(res.company); })
      .catch(() => {});
  }, []);

  return (
    <aside style={{
      width: '220px',
      backgroundColor: 'var(--bg-sidebar)',
      color: '#cbd5e1',
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      flexShrink: 0
    }}>
      {/* Brand */}
      <div style={{
        padding: '20px',
        borderBottom: '1px solid #1e293b',
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
      }}>
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '6px',
          background: 'linear-gradient(135deg, #2563eb, #1d4ed8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontWeight: '700',
          fontSize: '16px',
          flexShrink: 0
        }}>
          T
        </div>
        <div style={{ color: 'white', fontWeight: '600', fontSize: '15px', letterSpacing: '-0.02em' }}>
          Bank-to-Tally
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: '16px 12px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '10px 14px',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: isActive ? '600' : '400',
                color: isActive ? '#ffffff' : '#94a3b8',
                backgroundColor: isActive ? '#1e293b' : 'transparent',
                textDecoration: 'none',
                transition: 'all 0.15s ease'
              })}
            >
              <Icon size={18} />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer — Company Name */}
      <div style={{
        padding: '16px 20px',
        borderTop: '1px solid #1e293b',
        fontSize: '12px',
        color: '#64748b',
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }}>
        <Building2 size={15} />
        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {companyName}
        </span>
      </div>
    </aside>
  );
}
