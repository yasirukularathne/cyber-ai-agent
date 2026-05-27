import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';

const BASE = 'http://localhost:8000/api';

export default function LogUpload() {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('idle'); // idle | uploading | processing | success | error
  const [errorMsg, setErrorMsg] = useState('');
  const [summaryData, setSummaryData] = useState(null);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.name.endsWith('.csv')) {
        setFile(selectedFile);
        setUploadStatus('idle');
        setErrorMsg('');
      } else {
        setErrorMsg('Please select a valid CSV file.');
        setFile(null);
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploadStatus('uploading');
    setErrorMsg('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      // 1. Upload the CSV file
      const uploadRes = await axios.post(`${BASE}/upload-logs`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // 2. Trigger the pipeline prediction
      setUploadStatus('processing');
      const predictRes = await axios.post(`${BASE}/predict?filename=${uploadRes.data.filename}&debug=true`);
      
      setSummaryData(predictRes.data);
      setUploadStatus('success');
    } catch (err) {
      setUploadStatus('error');
      setErrorMsg(err.response?.data?.detail || 'An error occurred during file processing.');
    }
  };

  return (
    <div className="fade-in" style={{ maxWidth: '800px', margin: '40px auto 0' }}>
      <div className="card" style={{ padding: '40px', textAlign: 'center' }}>
        <h2 style={{ fontSize: '2rem', marginBottom: '12px' }}>Upload Network Traffic Logs</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '32px' }}>
          Select or drag a network PCAP-exported CSV log file to perform a layer-by-layer intrusion analysis.
        </p>

        {/* Upload Box Zone */}
        <div style={{
          border: '2px dashed var(--border-color)',
          borderRadius: '12px',
          padding: '40px 20px',
          background: 'rgba(9, 13, 22, 0.4)',
          cursor: 'pointer',
          position: 'relative',
          transition: 'all 0.2s',
          marginBottom: '24px'
        }}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const dropped = e.dataTransfer.files[0];
            if (dropped.name.endsWith('.csv')) {
              setFile(dropped);
              setUploadStatus('idle');
              setErrorMsg('');
            } else {
              setErrorMsg('Only CSV log files are supported.');
            }
          }
        }}>
          <input
            type="file"
            id="fileInput"
            accept=".csv"
            onChange={handleFileChange}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              opacity: 0,
              cursor: 'pointer'
            }}
          />
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
            <UploadCloud size={48} color="var(--color-primary)" style={{ opacity: 0.8 }} />
            {file ? (
              <div>
                <p style={{ fontWeight: 600, color: 'var(--text-main)' }}>{file.name}</p>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  {(file.size / 1024).toFixed(1)} KB
                </p>
              </div>
            ) : (
              <div>
                <p style={{ fontWeight: 600 }}>Click to browse or drag and drop your file here</p>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Only CICIDS2017 exported CSV format is supported.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Error Messages */}
        {errorMsg && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: 'rgba(255, 123, 114, 0.1)',
            border: '1px solid rgba(255, 123, 114, 0.2)',
            padding: '12px 16px',
            borderRadius: '8px',
            color: 'var(--color-danger)',
            fontSize: '0.9rem',
            textAlign: 'left',
            marginBottom: '24px'
          }}>
            <AlertCircle size={18} />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Action Button */}
        {uploadStatus === 'idle' && file && (
          <button onClick={handleUpload} className="btn btn-primary" style={{ width: '200px' }}>
            Analyze Logs
          </button>
        )}

        {/* Status Indicators */}
        {(uploadStatus === 'uploading' || uploadStatus === 'processing') && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px', padding: '10px 0' }}>
            <RefreshCw size={28} className="spin" style={{
              animation: 'spin 1.5s linear infinite',
              color: 'var(--color-primary)'
            }} />
            <p style={{ fontWeight: 600, color: 'var(--text-main)' }}>
              {uploadStatus === 'uploading' ? 'Uploading log file...' : 'Running 8-Layer AI Detection Pipeline...'}
            </p>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Extracting features, evaluating XGBoost/BERT/Autoencoder model outputs.
            </p>
          </div>
        )}

        {uploadStatus === 'success' && summaryData && (
          <div style={{
            backgroundColor: 'rgba(63, 185, 80, 0.08)',
            border: '1px solid rgba(63, 185, 80, 0.2)',
            borderRadius: '12px',
            padding: '24px',
            textAlign: 'left',
            marginTop: '20px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <CheckCircle2 size={24} color="var(--color-success)" />
              <h3 style={{ fontSize: '1.25rem' }}>Analysis Completed Successfully!</h3>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
              <div style={{ padding: '16px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px' }}>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Total Records Analyzed</p>
                <p style={{ fontSize: '1.8rem', fontWeight: 700 }}>{summaryData.total_records}</p>
              </div>
              <div style={{
                padding: '16px',
                background: summaryData.threats_detected > 0 ? 'rgba(255, 123, 114, 0.05)' : 'rgba(63, 185, 80, 0.05)',
                borderRadius: '8px',
                border: `1px solid ${summaryData.threats_detected > 0 ? 'rgba(255,123,114,0.1)' : 'rgba(63,185,80,0.1)'}`
              }}>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Intrusions Detected</p>
                <p style={{
                  fontSize: '1.8rem',
                  fontWeight: 700,
                  color: summaryData.threats_detected > 0 ? 'var(--color-danger)' : 'var(--color-success)'
                }}>
                  {summaryData.threats_detected}
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={() => navigate('/')}
                className="btn btn-primary"
                style={{ flex: 1 }}
              >
                Go to Dashboard
              </button>
              <button
                onClick={() => navigate('/debug')}
                className="btn btn-secondary"
                style={{ flex: 1 }}
              >
                Inspect Layer Debug Logs
              </button>
            </div>
          </div>
        )}
      </div>

      <style dangerouslySetInnerHTML={{__html: `
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}} />
    </div>
  );
}
