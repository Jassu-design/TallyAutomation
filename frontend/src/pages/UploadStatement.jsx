import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PageHeader from '../components/layout/PageHeader';
import UploadZone from '../components/imports/UploadZone';
import { BankAPI } from '../services/api';
import { useToast } from '../hooks/useToast';
import { CheckCircle2, FileText, ArrowRight } from 'lucide-react';

export default function UploadStatement() {
  const { showSuccess, showError } = useToast();
  const navigate = useNavigate();
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);

  const handleUpload = async (formData) => {
    setIsUploading(true);
    try {
      const res = await BankAPI.uploadStatement(formData);
      setUploadResult(res);
      showSuccess(res.message || 'Statement processed successfully.');
    } catch (err) {
      showError(err.message || 'Failed to process statement.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleTestInvoice = async () => {
    setIsUploading(true);
    try {
      const res = await BankAPI.processSampleInvoice();
      setUploadResult(res);
      showSuccess('Shree Ram Papad GST Invoice processed successfully!');
    } catch (err) {
      showError(err.message || 'Failed to process sample GST Invoice.');
    } finally {
      setIsUploading(false);
    }
  };

  if (uploadResult) {
    const total = uploadResult.transactions_found ?? uploadResult.total ?? 0;
    const review = uploadResult.review_needed ?? uploadResult.review ?? 0;

    return (
      <div style={{ maxWidth: '600px', margin: '0 auto' }}>
        <PageHeader title="Upload Bank Statement" subtitle="Statement processed successfully" />

        <div className="card" style={{ padding: '28px', textAlign: 'center' }}>
          <CheckCircle2 size={48} color="var(--success)" style={{ marginBottom: '16px' }} />
          <h2 style={{ fontSize: '20px', fontWeight: '700', marginBottom: '8px' }}>Upload Complete</h2>
          <p style={{ color: 'var(--text-muted)', marginBottom: '24px', fontSize: '14px' }}>
            {uploadResult.message || 'Your statement has been processed.'}
          </p>

          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '16px',
            marginBottom: '28px'
          }}>
            <div style={{
              background: 'var(--success-bg)',
              borderRadius: 'var(--radius-sm)',
              padding: '16px'
            }}>
              <div style={{ fontSize: '28px', fontWeight: '700', color: 'var(--success)' }}>{total}</div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>Transactions Found</div>
            </div>
            <div style={{
              background: '#fef3c7',
              borderRadius: 'var(--radius-sm)',
              padding: '16px'
            }}>
              <div style={{ fontSize: '28px', fontWeight: '700', color: '#d97706' }}>{review}</div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>Review Needed</div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
            <button className="btn btn-primary" onClick={() => navigate('/transactions')}>
              Go to Transactions <ArrowRight size={15} />
            </button>
            <button className="btn btn-secondary" onClick={() => setUploadResult(null)}>
              Upload Another
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '700px', margin: '0 auto' }}>
      <PageHeader
        title="Upload Bank Statement"
        subtitle="Ingest Excel (.xlsx, .xls), CSV (.csv), or PDF (.pdf) bank statements"
      />

      <UploadZone onUpload={handleUpload} isUploading={isUploading} />

      <div style={{ marginTop: '16px', textAlign: 'center' }}>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={handleTestInvoice}
          disabled={isUploading}
          style={{ borderColor: '#f59e0b', color: '#b45309' }}
        >
          <FileText size={14} color="#d97706" />
          Test GST Invoice (Shree Ram Papad)
        </button>
      </div>
    </div>
  );
}
