import { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, AlertTriangle, ShieldCheck, HelpCircle } from 'lucide-react';
import SeverityBadge from '../components/SeverityBadge';

const BASE = 'http://localhost:8000/api';

export default function Threats() {
  const [threats, setThreats] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    axios.get(`${BASE}/dashboard`)
      .then((res) => {
        if (res.data) {
          setThreats(res.data.recent_threats || []);
        }
        setLoading(false);
      })
      .catch(() => {
        setError(true);
        setLoading(false);
      });
  }, []);

  const filteredThreats = threats.filter(t => {
    const query = searchQuery.toLowerCase();
    return (
      t.ip.toLowerCase().includes(query) ||
      t.attack_type.toLowerCase().includes(query) ||
      t.severity.toLowerCase().includes(query)
    );
  });

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <p style={{ color: 'var(--text-muted)' }}>Loading threat vectors...</p>
      </div>
    );
  }

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div>
        <h2 style={{ fontSize: '1.8rem', marginBottom: '8px' }}>Security Intrusions Log</h2>
        <p style={{ color: 'var(--text-muted)' }}>
          Detailed record of all network flow anomalies classified as active threats by the model fusion engine.
        </p>
      </div>

      {/* Filter Toolbar */}
      <div className="card" style={{ padding: '16px 20px', display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <Search size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
          <input
            type="text"
            placeholder="Search threats by Source IP, Attack Vector, or Severity..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              backgroundColor: 'var(--bg-primary)',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              padding: '10px 12px 10px 40px',
              color: 'var(--text-main)',
              fontSize: '0.9rem',
              fontFamily: 'var(--font-family)',
              outline: 'none',
              transition: 'border-color 0.2s'
            }}
            onFocus={(e) => e.target.style.borderColor = 'rgba(88,166,255,0.6)'}
            onBlur={(e) => e.target.style.borderColor = 'var(--border-color)'}
          />
        </div>
      </div>

      {/* Threats Table Card */}
      <div className="card" style={{ padding: 0 }}>
        {filteredThreats.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '16px', fontWeight: 600 }}>INDEX</th>
                  <th style={{ padding: '16px', fontWeight: 600 }}>SOURCE IP</th>
                  <th style={{ padding: '16px', fontWeight: 600 }}>ATTACK TYPE</th>
                  <th style={{ padding: '16px', fontWeight: 600 }}>SEVERITY</th>
                  <th style={{ padding: '16px', fontWeight: 600 }}>XGB VIEW</th>
                  <th style={{ padding: '16px', fontWeight: 600 }}>BERT VIEW</th>
                  <th style={{ padding: '16px', fontWeight: 600 }}>AE ANOMALY</th>
                  <th style={{ padding: '16px', fontWeight: 600 }}>FUSED CRITERIA</th>
                </tr>
              </thead>
              <tbody>
                {filteredThreats.map((threat) => (
                  <tr key={threat.index} style={{ borderBottom: '1px solid rgba(48,54,61,0.2)', transition: 'background-color 0.2s' }}>
                    <td style={{ padding: '16px', color: 'var(--text-muted)' }}>#{threat.index}</td>
                    <td style={{ padding: '16px', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{threat.ip}</td>
                    <td style={{ padding: '16px', fontWeight: 600 }}>{threat.attack_type}</td>
                    <td style={{ padding: '16px' }}><SeverityBadge severity={threat.severity} /></td>
                    <td style={{ padding: '16px', color: 'var(--text-muted)' }}>{threat.xgb_prediction}</td>
                    <td style={{ padding: '16px', color: 'var(--text-muted)' }}>{threat.bert_prediction}</td>
                    <td style={{ padding: '16px' }}>
                      <span style={{
                        padding: '2px 8px',
                        borderRadius: '4px',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        backgroundColor: threat.ae_flagged ? 'rgba(255,123,114,0.1)' : 'rgba(63,185,80,0.1)',
                        color: threat.ae_flagged ? 'var(--color-danger)' : 'var(--color-success)',
                        border: `1px solid ${threat.ae_flagged ? 'rgba(255,123,114,0.2)' : 'rgba(63,185,80,0.2)'}`
                      }}>
                        {threat.ae_flagged ? 'FLAGGED' : 'NORMAL'}
                      </span>
                    </td>
                    <td style={{ padding: '16px', fontWeight: 700, color: 'var(--color-primary)' }}>{threat.confidence_pct}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
            {threats.length === 0 ? (
              <>
                <ShieldCheck size={48} color="var(--color-success)" style={{ opacity: 0.8 }} />
                <h3>No Malicious Entries Found</h3>
                <p style={{ maxWidth: '500px', margin: '0 auto', fontSize: '0.9rem' }}>
                  The last analysis did not identify any attacks. Your traffic remains clear of intrusion.
                </p>
              </>
            ) : (
              <>
                <HelpCircle size={48} style={{ opacity: 0.5 }} />
                <h3>No Matching Search Results</h3>
                <p style={{ fontSize: '0.9rem' }}>
                  No threats match the search term "{searchQuery}". Try editing the criteria.
                </p>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
