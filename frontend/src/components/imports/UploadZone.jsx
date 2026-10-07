import React, { useState, useRef } from 'react';
import { UploadCloud, FileSpreadsheet, Check, AlertCircle, Loader2 } from 'lucide-react';

export default function UploadZone({ onUpload, isUploading }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [bank, setBank] = useState('Auto Detect');
  const [company, setCompany] = useState('ABC Pvt Ltd');
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      validateAndSetFile(file);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (file) => {
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (['.csv', '.xlsx', '.xls', '.pdf'].includes(ext)) {
      setSelectedFile(file);
    } else {
      alert('Please upload a valid Excel (.xlsx, .xls), CSV (.csv), or PDF (.pdf) file.');
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('bank', bank);
    formData.append('company', company);

    onUpload(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="card" style={{ padding: '32px' }}>
      {/* Drag & Drop Area */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        style={{
          border: `2px dashed ${dragActive ? 'var(--primary)' : 'var(--border-color)'}`,
          borderRadius: 'var(--radius-md)',
          padding: '40px 24px',
          textAlign: 'center',
          backgroundColor: dragActive ? 'var(--primary-light)' : '#f8fafc',
          cursor: 'pointer',
          transition: 'all 0.15s ease-in-out',
          marginBottom: '24px'
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.xlsx,.xls,.pdf"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />

        <div style={{
          width: '56px',
          height: '56px',
          borderRadius: '50%',
          backgroundColor: 'white',
          boxShadow: 'var(--shadow-sm)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 16px auto',
          color: 'var(--primary)'
        }}>
          {selectedFile ? <FileSpreadsheet size={28} /> : <UploadCloud size={28} />}
        </div>

        {selectedFile ? (
          <div>
            <h4 style={{ fontSize: '15px', fontWeight: '600', color: 'var(--text-primary)' }}>
              {selectedFile.name}
            </h4>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
              {(selectedFile.size / 1024).toFixed(1)} KB — Click to change file
            </p>
          </div>
        ) : (
          <div>
            <h4 style={{ fontSize: '16px', fontWeight: '600', color: 'var(--text-primary)' }}>
              Drag & Drop Bank Statement Here
            </h4>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
              Supports Excel (.xlsx, .xls), CSV (.csv), and PDF (.pdf) statements
            </p>

            <div style={{ marginTop: '16px' }}>
              <span className="btn btn-secondary btn-sm" style={{ pointerEvents: 'none' }}>
                Choose File from Computer
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Selectors */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '16px',
        marginBottom: '24px'
      }}>
        <div className="form-group" style={{ margin: 0 }}>
          <label className="form-label">Bank Format</label>
          <select 
            className="select"
            value={bank}
            onChange={(e) => setBank(e.target.value)}
          >
            <option value="Auto Detect">Auto Detect Bank Format</option>
            <option value="HDFC Bank">HDFC Bank</option>
            <option value="ICICI Bank">ICICI Bank</option>
            <option value="State Bank of India">State Bank of India</option>
            <option value="Axis Bank">Axis Bank</option>
            <option value="Generic Bank">Generic Format</option>
          </select>
        </div>

        <div className="form-group" style={{ margin: 0 }}>
          <label className="form-label">Tally Company</label>
          <select 
            className="select"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
          >
            <option value="ABC Pvt Ltd">ABC Pvt Ltd</option>
            <option value="XYZ Enterprises">XYZ Enterprises</option>
          </select>
        </div>
      </div>

      {/* Submit Button */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
        {selectedFile && (
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => setSelectedFile(null)}
            disabled={isUploading}
          >
            Clear
          </button>
        )}
        <button
          type="submit"
          className="btn btn-primary"
          disabled={!selectedFile || isUploading}
          style={{ minWidth: '160px', justifyContent: 'center' }}
        >
          {isUploading ? (
            <>
              <Loader2 size={16} className="spin" />
              Processing Statement...
            </>
          ) : (
            'Process Statement'
          )}
        </button>
      </div>
    </form>
  );
}
