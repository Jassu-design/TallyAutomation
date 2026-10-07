import React, { useState, useEffect } from 'react';
import PageHeader from '../components/layout/PageHeader';
import MappingTable from '../components/mappings/MappingTable';
import MappingForm from '../components/mappings/MappingForm';
import LoadingState from '../components/common/LoadingState';
import { MappingAPI, TallyAPI } from '../services/api';
import { useToast } from '../hooks/useToast';
import { Plus, Search, Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';

export default function LedgerMappings() {
  const { showSuccess, showError } = useToast();
  const [mappings, setMappings] = useState([]);
  const [ledgers, setLedgers] = useState([]);
  const [loading, setLoading] = useState(true);

  // Form modal state
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingRule, setEditingRule] = useState(null);

  // Real-time Tester State (Section 14.1)
  const [testDescription, setTestDescription] = useState('UPI/AMAZON PAY INDIA/ORDER491');
  const [testType, setTestType] = useState('DEBIT');
  const [testResult, setTestResult] = useState(null);
  const [testing, setTesting] = useState(false);

  const fetchMappings = async () => {
    try {
      setLoading(true);
      const res = await MappingAPI.getMappings();
      setMappings(res || []);
    } catch (err) {
      showError(err.message || 'Failed to load mappings.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMappings();
    const fetchLedgers = async () => {
      try {
        const list = await TallyAPI.getLedgers();
        setLedgers(list || []);
      } catch (e) {
        console.error(e);
      }
    };
    fetchLedgers();
  }, []);

  const handleTestRule = async () => {
    if (!testDescription.trim()) return;
    setTesting(true);
    try {
      const res = await MappingAPI.testMapping({
        description: testDescription,
        transaction_type: testType
      });
      setTestResult(res);
    } catch (err) {
      showError(err.message || 'Test failed.');
    } finally {
      setTesting(false);
    }
  };

  // Run test automatically when query changes
  useEffect(() => {
    const timer = setTimeout(() => {
      handleTestRule();
    }, 300);
    return () => clearTimeout(timer);
  }, [testDescription, testType, mappings]);

  const handleSaveRule = async (data) => {
    try {
      if (editingRule) {
        await MappingAPI.updateMapping(editingRule.id, data);
        showSuccess('Mapping rule updated.');
      } else {
        await MappingAPI.createMapping(data);
        showSuccess('New mapping rule created.');
      }
      setIsFormOpen(false);
      setEditingRule(null);
      fetchMappings();
    } catch (err) {
      showError(err.message || 'Failed to save rule.');
    }
  };

  const handleDeleteRule = async (id) => {
    if (!window.confirm(`Are you sure you want to delete mapping rule #${id}?`)) return;
    try {
      await MappingAPI.deleteMapping(id);
      showSuccess('Mapping rule deleted.');
      fetchMappings();
    } catch (err) {
      showError(err.message || 'Failed to delete rule.');
    }
  };

  const handleToggleActive = async (rule) => {
    try {
      await MappingAPI.updateMapping(rule.id, { active: !rule.active });
      showSuccess(`Rule '${rule.keyword}' ${!rule.active ? 'activated' : 'disabled'}.`);
      fetchMappings();
    } catch (err) {
      showError(err.message || 'Failed to toggle status.');
    }
  };

  return (
    <div>
      <PageHeader
        title="Ledger Mappings"
        subtitle="Keyword and pattern matching rules for automated TallyPrime ledger & voucher classification"
        actions={
          <button 
            className="btn btn-primary"
            onClick={() => {
              setEditingRule(null);
              setIsFormOpen(true);
            }}
          >
            <Plus size={16} /> Add Mapping Rule
          </button>
        }
      />

      {/* Interactive Rule Tester (Section 14.1) */}
      <div className="card" style={{ padding: '20px', marginBottom: '24px', backgroundColor: '#f8fafc' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
          <Sparkles size={16} color="var(--primary)" />
          <h3 style={{ fontSize: '14px', fontWeight: '600' }}>Interactive Mapping Rule Tester</h3>
        </div>
        <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '14px' }}>
          Enter a sample bank statement description below to preview which rule matches and what Tally ledger is assigned:
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '12px', marginBottom: '14px' }}>
          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Sample Bank Narration</label>
            <input
              type="text"
              className="input"
              value={testDescription}
              onChange={(e) => setTestDescription(e.target.value)}
              placeholder="e.g. UPI/RELIANCE JIO RECHARGE/99120"
            />
          </div>

          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Transaction Type</label>
            <select
              className="select"
              value={testType}
              onChange={(e) => setTestType(e.target.value)}
            >
              <option value="DEBIT">Debit (Withdrawal)</option>
              <option value="CREDIT">Credit (Deposit)</option>
            </select>
          </div>
        </div>

        {testResult && (
          <div style={{
            background: testResult.matched ? 'var(--success-bg)' : '#fffbeb',
            border: `1px solid ${testResult.matched ? 'var(--success-border)' : '#fef3c7'}`,
            borderRadius: 'var(--radius-sm)',
            padding: '12px 16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '13px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              {testResult.matched ? (
                <CheckCircle2 size={18} color="var(--success)" />
              ) : (
                <AlertCircle size={18} color="var(--warning)" />
              )}
              <div>
                <strong>
                  {testResult.matched ? `Matched Rule: "${testResult.matched_keyword}"` : 'No Custom Rule Matched (Fallback)'}
                </strong>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  Target Ledger: <strong>{testResult.suggested_ledger || 'Unassigned / Needs Review'}</strong> • Voucher: <strong>{testResult.suggested_voucher}</strong>
                </div>
              </div>
            </div>

            <div style={{ textAlign: 'right' }}>
              <span style={{
                fontSize: '11px',
                fontWeight: '700',
                padding: '3px 8px',
                borderRadius: '4px',
                backgroundColor: testResult.confidence >= 0.9 ? 'var(--success)' : 'var(--warning)',
                color: 'white'
              }}>
                Confidence: {Math.round(testResult.confidence * 100)}%
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Rules Table */}
      {loading ? (
        <LoadingState message="Loading mapping rules..." />
      ) : (
        <MappingTable
          mappings={mappings}
          onEdit={(rule) => {
            setEditingRule(rule);
            setIsFormOpen(true);
          }}
          onDelete={handleDeleteRule}
          onToggleActive={handleToggleActive}
        />
      )}

      {/* Add / Edit Form Modal */}
      <MappingForm
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setEditingRule(null);
        }}
        onSave={handleSaveRule}
        editingRule={editingRule}
        ledgers={ledgers}
      />
    </div>
  );
}
