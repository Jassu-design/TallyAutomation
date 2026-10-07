import React, { useState, useEffect } from 'react';
import PageHeader from '../components/layout/PageHeader';
import LoadingState from '../components/common/LoadingState';
import { SettingsAPI } from '../services/api';
import { useToast } from '../hooks/useToast';
import { Save, Server, Sliders, Shield } from 'lucide-react';

export default function Settings() {
  const { showSuccess, showError } = useToast();
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setLoading(true);
        const res = await SettingsAPI.getSettings();
        setConfig(res);
      } catch (err) {
        showError(err.message || 'Failed to load configuration.');
      } finally {
        setLoading(false);
      }
    };
    fetchSettings();
  }, []);

  const handleChange = (key, val) => {
    setConfig((prev) => ({ ...prev, [key]: val }));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await SettingsAPI.updateSettings(config);
      setConfig(res.settings);
      showSuccess('Application configuration saved successfully.');
    } catch (err) {
      showError(err.message || 'Failed to save configuration.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <LoadingState message="Loading settings..." />;

  return (
    <div style={{ maxWidth: '720px' }}>
      <PageHeader
        title="Application Settings"
        subtitle="Manage TallyPrime connection parameters, automation thresholds, and defaults"
      />

      <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {/* TallyPrime Integration Parameters */}
        <div className="card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <Server size={18} color="var(--primary)" />
            <h3 style={{ fontSize: '15px', fontWeight: '600' }}>TallyPrime Integration</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '16px', marginBottom: '16px' }}>
            <div className="form-group" style={{ margin: 0 }}>
              <label className="form-label">Tally Host / IP</label>
              <input
                type="text"
                className="input"
                value={config.tally_host || ''}
                onChange={(e) => handleChange('tally_host', e.target.value)}
              />
            </div>

            <div className="form-group" style={{ margin: 0 }}>
              <label className="form-label">Tally XML Port</label>
              <input
                type="number"
                className="input"
                value={config.tally_port || 9000}
                onChange={(e) => handleChange('tally_port', parseInt(e.target.value))}
              />
            </div>
          </div>

          <div className="form-group" style={{ margin: 0, marginBottom: '16px' }}>
            <label className="form-label">Active Tally Company Name</label>
            <input
              type="text"
              className="input"
              value={config.tally_company || ''}
              onChange={(e) => handleChange('tally_company', e.target.value)}
            />
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              Must match the exact company name loaded in TallyPrime.
            </span>
          </div>

          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Default Bank Ledger in Tally</label>
            <input
              type="text"
              className="input"
              value={config.default_bank_ledger || ''}
              onChange={(e) => handleChange('default_bank_ledger', e.target.value)}
            />
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              The balancing bank ledger credited/debited on voucher import.
            </span>
          </div>
        </div>

        {/* Automation & Safety */}
        <div className="card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <Shield size={18} color="var(--primary)" />
            <h3 style={{ fontSize: '15px', fontWeight: '600' }}>Automation & Safety Rules</h3>
          </div>

          <div className="form-group" style={{ margin: 0, marginBottom: '16px' }}>
            <label className="form-label">Auto-Approval Confidence Threshold (0.50 - 1.00)</label>
            <input
              type="number"
              step="0.05"
              min="0.50"
              max="1.00"
              className="input"
              value={config.auto_approve_threshold || 0.95}
              onChange={(e) => handleChange('auto_approve_threshold', parseFloat(e.target.value))}
            />
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              Transactions matching rules with confidence above this score are auto-approved; lower enters Review Queue.
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <input
              type="checkbox"
              id="sim-mode"
              checked={config.tally_simulation_mode || false}
              onChange={(e) => handleChange('tally_simulation_mode', e.target.checked)}
            />
            <label htmlFor="sim-mode" style={{ fontSize: '13px', cursor: 'pointer' }}>
              Enable TallyPrime Simulation Gateway (Emulate responses without live Tally instance)
            </label>
          </div>
        </div>

        {/* Save Button */}
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            <Save size={14} /> {saving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </form>
    </div>
  );
}
