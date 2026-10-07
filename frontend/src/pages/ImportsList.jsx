import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import PageHeader from '../components/layout/PageHeader';
import LoadingState from '../components/common/LoadingState';
import EmptyState from '../components/common/EmptyState';
import Badge from '../components/common/Badge';
import { BankAPI } from '../services/api';
import { useToast } from '../hooks/useToast';
import { UploadCloud, Eye, Trash2, ArrowRight } from 'lucide-react';

export default function ImportsList() {
  const navigate = useNavigate();
  const { showSuccess, showError } = useToast();
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchImports = async () => {
    try {
      setLoading(true);
      const res = await BankAPI.getImports();
      setBatches(res.items || []);
    } catch (err) {
      showError(err.message || 'Failed to load imports.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchImports();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm(`Delete import batch #${id} and all its transactions?`)) return;
    try {
      await BankAPI.deleteImport(id);
      showSuccess(`Batch #${id} deleted.`);
      fetchImports();
    } catch (err) {
      showError(err.message || 'Failed to delete batch.');
    }
  };

  return (
    <div>
      <PageHeader
        title="Statement Batches"
        subtitle="Historical list of uploaded bank statements and their processing statuses"
        actions={
          <button 
            className="btn btn-primary"
            onClick={() => navigate('/imports/upload')}
          >
            <UploadCloud size={16} /> Upload Statement
          </button>
        }
      />

      {loading ? (
        <LoadingState message="Loading statement batches..." />
      ) : batches.length === 0 ? (
        <div className="card">
          <EmptyState
            title="No Statements Uploaded"
            description="Upload an Excel (.xlsx, .xls) or CSV statement to begin automated processing."
            action={
              <button 
                className="btn btn-primary"
                onClick={() => navigate('/imports/upload')}
              >
                Upload First Statement
              </button>
            }
          />
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Batch #</th>
                <th>File Name</th>
                <th>Bank</th>
                <th style={{ textAlign: 'right' }}>Total</th>
                <th style={{ textAlign: 'right' }}>Posted</th>
                <th style={{ textAlign: 'right' }}>Review</th>
                <th style={{ textAlign: 'right' }}>Duplicates</th>
                <th>Uploaded At</th>
                <th>Status</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {batches.map((b) => (
                <tr key={b.id}>
                  <td><strong>#{b.id}</strong></td>
                  <td style={{ fontWeight: '500' }}>{b.filename}</td>
                  <td>{b.bank_name}</td>
                  <td style={{ textAlign: 'right', fontWeight: '600' }}>{b.total_transactions}</td>
                  <td style={{ textAlign: 'right', color: 'var(--success)', fontWeight: '600' }}>{b.posted_transactions}</td>
                  <td style={{ textAlign: 'right', color: 'var(--warning)', fontWeight: '600' }}>{b.review_transactions}</td>
                  <td style={{ textAlign: 'right', color: 'var(--duplicate)', fontWeight: '600' }}>{b.duplicate_transactions}</td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '12px' }}>{b.uploaded_at}</td>
                  <td>
                    <Badge status={b.status} />
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <div style={{ display: 'inline-flex', gap: '6px' }}>
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => navigate(`/imports/${b.id}`)}
                        title="View Batch Details"
                      >
                        <Eye size={13} />
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(b.id)}
                        title="Delete Batch"
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
