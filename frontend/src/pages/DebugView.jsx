import { useState, useEffect } from 'react';
import axios from 'axios';
import { Terminal, Database, Cpu, HelpCircle, Layers, CheckCircle2, ChevronRight } from 'lucide-react';

const BASE = 'http://localhost:8000/api';

const LAYER_ORDER = [
  'ingestion', 'preprocessing', 'xgboost', 'bert',
  'autoencoder', 'fusion', 'mcp', 'llm'
];

const LAYER_LABELS = {
  ingestion:     '1 · Data Ingestion',
  preprocessing: '2 · Preprocessing + NLP',
  xgboost:       '3 · XGBoost Classifier',
  bert:          '4 · BERT Transformer',
  autoencoder:   '5 · Autoencoder (AE)',
  fusion:        '6 · Decision Fusion',
  mcp:           '7 · MCP Enrichment',
  llm:           '8 · LLM Explanation',
};

export default function DebugView() {
  const [runs, setRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState('');
  const [debugData, setDebugData] = useState(null);
  const [selectedLayer, setSelectedLayer] = useState('ingestion');
  const [loading, setLoading] = useState(true);

  // 1. Fetch available runs
  useEffect(() => {
    axios.get(`${BASE}/debug/runs`)
      .then((res) => {
        if (res.data && res.data.runs && res.data.runs.length > 0) {
          setRuns(res.data.runs);
          setSelectedRun(res.data.runs[0]); // Default to latest run
        } else {
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error("Error fetching debug runs:", err);
        setLoading(false);
      });
  }, []);

  // 2. Fetch specific run data when selectedRun changes
  useEffect(() => {
    if (!selectedRun) return;
    setLoading(true);
    axios.get(`${BASE}/debug/run/${selectedRun}`)
      .then((res) => {
        setDebugData(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching debug run:", err);
        setLoading(false);
      });
  }, [selectedRun]);

  if (loading && !debugData) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <p style={{ color: 'var(--text-muted)' }}>Loading model pipeline execution telemetry...</p>
      </div>
    );
  }

  if (runs.length === 0 || !debugData) {
    return (
      <div className="card fade-in" style={{ textAlign: 'center', padding: '60px 40px', maxWidth: '700px', margin: '60px auto 0' }}>
        <div style={{
          background: 'rgba(88, 166, 255, 0.05)',
          padding: '24px',
          borderRadius: '50%',
          display: 'inline-block',
          marginBottom: '24px'
        }}>
          <Terminal size={48} color="var(--color-primary)" />
        </div>
        <h2 style={{ fontSize: '1.8rem', marginBottom: '12px' }}>Telemetry Stream Offline</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '24px' }}>
          No historical pipeline runs were found in the database. Run an analysis on a network log file to inspect the intermediate layer outputs.
        </p>
      </div>
    );
  }

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Header bar with run selector */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2 style={{ fontSize: '1.8rem', marginBottom: '4px' }}>8-Layer Telemetry</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Layer-by-layer diagnostic stream of the hybrid AI model pipeline.
          </p>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)' }}>SELECT PIPELINE RUN:</span>
          <select
            value={selectedRun}
            onChange={(e) => setSelectedRun(e.target.value)}
            style={{
              backgroundColor: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-main)',
              padding: '8px 12px',
              borderRadius: '6px',
              fontSize: '0.9rem',
              fontWeight: 600,
              outline: 'none',
              cursor: 'pointer'
            }}
          >
            {runs.map(run => (
              <option key={run} value={run}>Run {run}</option>
            ))}
          </select>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gap: '24px', alignItems: 'start' }}>
        
        {/* Left Side: Layer Tabs */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {LAYER_ORDER.map(layer => {
            const isSelected = selectedLayer === layer;
            const layerData = debugData.layers?.[layer] || {};
            const isOk = layerData.status === 'OK';
            
            return (
              <button
                key={layer}
                onClick={() => setSelectedLayer(layer)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '14px 16px',
                  borderRadius: '8px',
                  border: `1px solid ${isSelected ? 'rgba(88,166,255,0.4)' : 'var(--border-color)'}`,
                  backgroundColor: isSelected ? 'rgba(56,139,253,0.1)' : 'var(--bg-card)',
                  color: isSelected ? 'var(--text-main)' : 'var(--text-muted)',
                  cursor: 'pointer',
                  textAlign: 'left',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  transition: 'all 0.2s cubic-bezier(0.16, 1, 0.3, 1)'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    backgroundColor: isOk ? 'var(--color-success)' : 'var(--color-danger)',
                    boxShadow: `0 0 6px ${isOk ? 'var(--color-success)' : 'var(--color-danger)'}`
                  }} />
                  <span>{LAYER_LABELS[layer]}</span>
                </div>
                <ChevronRight size={14} style={{ opacity: isSelected ? 0.8 : 0.3 }} />
              </button>
            );
          })}
        </div>

        {/* Right Side: Raw JSON Output & Diagnostics */}
        <div className="card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px', minHeight: '520px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px' }}>
            <h3 style={{ fontSize: '1.2rem', color: 'var(--color-primary)' }}>
              {LAYER_LABELS[selectedLayer]} Diagnostic Data
            </h3>
            {(() => {
              const layerStatus = debugData.layers?.[selectedLayer]?.status;
              const isOk = layerStatus === 'OK';
              return (
                <span className={isOk ? 'badge badge-success' : 'badge badge-critical'}>
                  {layerStatus ? `Execution: ${layerStatus}` : 'No Data'}
                </span>
              );
            })()}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Output payload transmitted to downstream pipeline layers:
            </p>
            
            <pre style={{
              backgroundColor: 'rgba(0,0,0,0.5)',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              padding: '16px',
              color: '#d1f1a5', // Terminal green text
              fontFamily: 'var(--font-mono)',
              fontSize: '0.8rem',
              overflow: 'auto',
              maxHeight: '440px',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-all'
            }}>
              {debugData.layers && debugData.layers[selectedLayer] ? (
                JSON.stringify(debugData.layers[selectedLayer], null, 2)
              ) : (
                "// No diagnostic data recorded for this layer."
              )}
            </pre>
          </div>
        </div>

      </div>

    </div>
  );
}
