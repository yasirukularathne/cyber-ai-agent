import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { 
  ShieldAlert, ShieldCheck, Activity, BarChart3, Database, 
  Clock, AlertTriangle, ArrowRight, Eye, PlaySquare
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, 
  ResponsiveContainer, PieChart, Pie, Cell, Legend
} from 'recharts';
import SeverityBadge from '../components/SeverityBadge';
import ModelBreakdown from '../components/ModelBreakdown';

const BASE = 'http://localhost:8000/api';

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    axios.get(`${BASE}/dashboard`)
      .then((res) => {
        if (res.data && res.data.run_id) {
          setData(res.data);
          setError(false);
        } else {
          // No analysis run yet
          setData(null);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("Dashboard error:", err);
        setError(true);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>Loading threat intelligence matrix...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="card fade-in" style={{ textAlign: 'center', padding: '60px 40px', maxWidth: '700px', margin: '60px auto 0' }}>
        <div style={{
          background: 'rgba(88, 166, 255, 0.05)',
          padding: '24px',
          borderRadius: '50%',
          display: 'inline-block',
          marginBottom: '24px'
        }}>
          <Activity size={48} color="var(--color-primary)" />
        </div>
        <h2 style={{ fontSize: '1.8rem', marginBottom: '12px' }}>No Intrusion Analysis Data Found</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '32px' }}>
          To view security event metrics, please upload a network traffic CSV log file first and execute the detection pipeline.
        </p>
        <button onClick={() => navigate('/upload')} className="btn btn-primary">
          <PlaySquare size={18} />
          <span>Upload and Analyze Logs</span>
        </button>
      </div>
    );
  }

  // Pre-process chart data
  const severityChartData = Object.entries(data.severity_counts || {}).map(([key, val]) => ({
    name: key,
    value: val
  }));

  const attackChartData = Object.entries(data.attack_counts || {}).map(([key, val]) => ({
    name: key,
    value: val
  })).filter(item => item.name !== 'Benign');

  const COLORS = ['#ff7b72', '#f2a629', '#38d3e8', '#c59eff', '#8b949e'];

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Run Summary Alert */}
      <div style={{
        background: data.threat_count > 0 ? 'rgba(255, 123, 114, 0.08)' : 'rgba(63, 185, 80, 0.08)',
        border: `1px solid ${data.threat_count > 0 ? 'rgba(255, 123, 114, 0.2)' : 'rgba(63, 185, 80, 0.2)'}`,
        borderRadius: '12px',
        padding: '18px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            background: data.threat_count > 0 ? 'rgba(255, 123, 114, 0.15)' : 'rgba(63, 185, 80, 0.15)',
            padding: '10px',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            {data.threat_count > 0 ? (
              <ShieldAlert size={22} color="var(--color-danger)" />
            ) : (
              <ShieldCheck size={22} color="var(--color-success)" />
            )}
          </div>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>
              {data.threat_count > 0 
                ? `${data.threat_count} Security Intrusions Flagged` 
                : 'Zero Threat Anomalies Detected'}
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Last analysis run ID: <code style={{ color: 'var(--color-primary)' }}>{data.run_id}</code>. Tested against the 8-layer architecture.
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <Link to="/debug" className="btn btn-secondary" style={{ fontSize: '0.8rem', padding: '8px 16px' }}>
            <Eye size={14} />
            <span>Trace Layers</span>
          </Link>
          {data.threat_count > 0 && (
            <Link to="/threats" className="btn btn-primary" style={{ fontSize: '0.8rem', padding: '8px 16px' }}>
              <span>View Threats</span>
              <ArrowRight size={14} />
            </Link>
          )}
        </div>
      </div>

      {/* Grid: Stat Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '20px'
      }}>
        <div className="card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>TOTAL RECORDS</span>
            <Database size={18} color="var(--color-primary)" />
          </div>
          <p style={{ fontSize: '1.85rem', fontWeight: 800 }}>{data.total_records.toLocaleString()}</p>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Network flows ingested
          </p>
        </div>

        <div className="card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>INTRUSIONS DETECTED</span>
            <AlertTriangle size={18} color={data.threat_count > 0 ? "var(--color-danger)" : "var(--color-success)"} />
          </div>
          <p style={{ fontSize: '1.85rem', fontWeight: 800, color: data.threat_count > 0 ? 'var(--color-danger)' : 'var(--text-main)' }}>
            {data.threat_count.toLocaleString()}
          </p>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Correlated across XGBoost + BERT
          </p>
        </div>

        <div className="card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>ATTACK RATIO</span>
            <Activity size={18} color="var(--color-secondary)" />
          </div>
          <p style={{ fontSize: '1.85rem', fontWeight: 800 }}>
            {data.total_records > 0 ? ((data.threat_count / data.total_records) * 100).toFixed(2) : 0}%
          </p>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Of total network bandwidth logs
          </p>
        </div>

        <div className="card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>PIPELINE PIPING</span>
            <BarChart3 size={18} color="var(--color-info)" />
          </div>
          <p style={{ fontSize: '1.85rem', fontWeight: 800 }}>8 / 8</p>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Verification layers online
          </p>
        </div>
      </div>

      {/* Grid: Charts */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: '20px'
      }}>
        {/* Severity chart */}
        <div className="card" style={{ height: '380px', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '20px' }}>Threat Severity Breakdown</h3>
          <div style={{ flex: 1 }}>
            {severityChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={severityChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                  <YAxis stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#161b22', borderColor: 'var(--border-color)', borderRadius: '8px' }}
                    labelStyle={{ color: 'var(--text-main)', fontWeight: 700 }}
                  />
                  <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                    {severityChartData.map((entry, index) => {
                      let color = 'var(--text-muted)';
                      if (entry.name === 'CRITICAL') color = 'var(--color-danger)';
                      else if (entry.name === 'HIGH') color = 'var(--color-warning)';
                      else if (entry.name === 'MEDIUM') color = 'var(--color-info)';
                      else if (entry.name === 'NONE') color = 'var(--color-success)';
                      return <Cell key={`cell-${index}`} fill={color} />;
                    })}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No severity data.</p>
              </div>
            )}
          </div>
        </div>

        {/* Attack Vector distribution */}
        <div className="card" style={{ height: '380px', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '20px' }}>Intrusion Vector Breakdown</h3>
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {attackChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={attackChartData}
                    cx="50%"
                    cy="45%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {attackChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#161b22', borderColor: 'var(--border-color)', borderRadius: '8px' }}
                  />
                  <Legend 
                    verticalAlign="bottom" 
                    height={36} 
                    iconType="circle"
                    formatter={(value) => <span style={{ color: 'var(--text-main)', fontSize: '12px' }}>{value}</span>}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', flexDirection: 'column', gap: '8px' }}>
                <ShieldCheck size={36} color="var(--color-success)" style={{ opacity: 0.8 }} />
                <p style={{ color: 'var(--color-success)', fontWeight: 600, fontSize: '0.9rem' }}>No malicious vectors active.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <ModelBreakdown />

      {/* Recent Threats Table */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3 style={{ fontSize: '1.1rem' }}>Identified Intrusions</h3>
          {data.recent_threats.length > 10 && (
            <Link to="/threats" style={{ fontSize: '0.85rem', color: 'var(--color-primary)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <span>View all threats</span>
              <ArrowRight size={14} />
            </Link>
          )}
        </div>

        {data.recent_threats.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>SOURCE IP</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>VECTOR TYPE</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>SEVERITY</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>XGB CONF</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>BERT CONF</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>ANOMALY SCORE</th>
                  <th style={{ padding: '12px 16px', fontWeight: 600 }}>FUSED RISK</th>
                </tr>
              </thead>
              <tbody>
                {data.recent_threats.map((threat) => (
                  <tr key={threat.index} style={{ borderBottom: '1px solid rgba(48,54,61,0.2)', transition: 'background-color 0.2s' }}>
                    <td style={{ padding: '12px 16px', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{threat.ip}</td>
                    <td style={{ padding: '12px 16px', fontWeight: 600 }}>{threat.attack_type}</td>
                    <td style={{ padding: '12px 16px' }}><SeverityBadge severity={threat.severity} /></td>
                    <td style={{ padding: '12px 16px', color: 'var(--text-muted)' }}>{threat.xgb_prediction}</td>
                    <td style={{ padding: '12px 16px', color: 'var(--text-muted)' }}>{threat.bert_prediction}</td>
                    <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>{threat.anomaly_score.toFixed(4)}</td>
                    <td style={{ padding: '12px 16px', fontWeight: 700, color: 'var(--color-primary)' }}>{threat.confidence_pct}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
            <ShieldCheck size={36} color="var(--color-success)" style={{ opacity: 0.8 }} />
            <p>No threats flagged. The system indicates a benign operational state.</p>
          </div>
        )}
      </div>

    </div>
  );
}
