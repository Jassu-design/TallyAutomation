import React, { useState, useEffect } from 'react';
import Modal from '../common/Modal';

export default function MappingForm({ isOpen, onClose, onSave, editingRule, ledgers = [] }) {
  const [keyword, setKeyword] = useState('');
  const [ledgerName, setLedgerName] = useState('');
  const [customLedger, setCustomLedger] = useState('');
  const [voucherType, setVoucherType] = useState('Payment');
  const [priority, setPriority] = useState(1);
  const [active, setActive] = useState(true);
  const [useCustomLedger, setUseCustomLedger] = useState(false);

  useEffect(() => {
    if (editingRule) {
      setKeyword(editingRule.keyword || '');
      setLedgerName(editingRule.ledger_name || '');
      setVoucherType(editingRule.voucher_type || 'Payment');
      setPriority(editingRule.priority !== undefined ? editingRule.priority : 1);
      setActive(editingRule.active !== undefined ? editingRule.active : true);
      setUseCustomLedger(false);
    } else {
      setKeyword('');
      setLedgerName('');
      setCustomLedger('');
      setVoucherType('Payment');
      setPriority(1);
      setActive(true);
      setUseCustomLedger(false);
    }
  }, [editingRule, isOpen]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const finalLedger = useCustomLedger ? customLedger.trim() : ledgerName;
    if (!keyword.trim() || !finalLedger) {
      alert('Please provide a keyword and target ledger name.');
      return;
    }

    onSave({
      keyword: keyword.trim().toUpperCase(),
      ledger_name: finalLedger,
      voucher_type: voucherType,
      priority: parseInt(priority) || 1,
      active
    });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={editingRule ? 'Edit Mapping Rule' : 'Add New Ledger Mapping'}
      footer={
        <>
          <button type="button" className="btn btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button type="button" className="btn btn-primary" onClick={handleSubmit}>
            {editingRule ? 'Save Changes' : 'Create Rule'}
          </button>
        </>
      }
    >
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        <div className="form-group" style={{ margin: 0 }}>
          <label className="form-label">Keyword / Search Pattern *</label>
          <input
            type="text"
            className="input"
            placeholder="e.g. AMAZON, JIO, AIRTEL, BESCOM"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            required
          />
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            Transactions containing this text will map to the designated ledger.
          </span>
        </div>

        <div className="form-group" style={{ margin: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <label className="form-label">Tally Ledger *</label>
            <button
              type="button"
              onClick={() => setUseCustomLedger(!useCustomLedger)}
              style={{ background: 'none', border: 'none', color: 'var(--primary)', fontSize: '11px', cursor: 'pointer' }}
            >
              {useCustomLedger ? 'Pick from list' : '+ Enter custom ledger'}
            </button>
          </div>

          {useCustomLedger ? (
            <input
              type="text"
              className="input"
              placeholder="Enter exact Tally ledger name"
              value={customLedger}
              onChange={(e) => setCustomLedger(e.target.value)}
            />
          ) : (
            <select
              className="select"
              value={ledgerName}
              onChange={(e) => setLedgerName(e.target.value)}
            >
              <option value="">-- Select Tally Ledger --</option>
              {ledgers.map((l) => (
                <option key={l.name} value={l.name}>
                  {l.name} ({l.group})
                </option>
              ))}
            </select>
          )}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Voucher Type</label>
            <select
              className="select"
              value={voucherType}
              onChange={(e) => setVoucherType(e.target.value)}
            >
              <option value="Payment">Payment</option>
              <option value="Receipt">Receipt</option>
              <option value="Contra">Contra</option>
              <option value="Journal">Journal</option>
            </select>
          </div>

          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Priority (1-10)</label>
            <input
              type="number"
              min="1"
              max="20"
              className="input"
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
            />
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '6px' }}>
          <input
            type="checkbox"
            id="active-check"
            checked={active}
            onChange={(e) => setActive(e.target.checked)}
          />
          <label htmlFor="active-check" style={{ fontSize: '13px', cursor: 'pointer' }}>
            Rule is Active
          </label>
        </div>
      </form>
    </Modal>
  );
}
