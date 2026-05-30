import { Link, useLocation } from 'react-router-dom';
import { Shield, LayoutDashboard, UploadCloud, AlertTriangle, Cpu, Terminal, BrainCircuit, Activity, BarChart3 } from 'lucide-react';

export default function Navbar() {
  const location = useLocation();

  const links = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/upload', label: 'Upload Logs', icon: UploadCloud },
    { path: '/threats', label: 'Threats', icon: AlertTriangle },
    { path: '/reports', label: 'AI Reports', icon: Cpu },
    { path: '/debug', label: 'Debug View', icon: Terminal },
    { path: '/xgboost-check', label: 'XGBoost', icon: BarChart3 },
    { path: '/bert-check', label: 'BERT', icon: BrainCircuit },
    { path: '/autoencoder-check', label: 'Autoencoder', icon: Activity },
  ];

  return (
    <nav style={{
      background: 'rgba(13, 17, 23, 0.75)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid rgba(48, 54, 61, 0.5)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      padding: '0 24px',
      height: '70px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between'
    }}>
      {/* Brand Logo */}
      <Link to="/" style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        textDecoration: 'none',
        color: 'var(--text-main)'
      }}>
        <div style={{
          background: 'linear-gradient(135deg, #1f6feb 0%, #58a6ff 100%)',
          padding: '8px',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 15px rgba(88, 166, 255, 0.3)'
        }}>
          <Shield size={20} color="#fff" />
        </div>
        <div>
          <h1 style={{ fontSize: '1.2rem', fontWeight: 800, letterSpacing: '-0.02em', margin: 0 }}>
            CYBER<span style={{ color: 'var(--color-primary)' }}>AI</span>
          </h1>
          <p style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.1em', marginTop: '-2px' }}>
            THREAT DETECTION V2
          </p>
        </div>
      </Link>

      {/* Navigation Links */}
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', justifyContent: 'center' }}>
        {links.map((link) => {
          const Icon = link.icon;
          const isActive = location.pathname === link.path;
          return (
            <Link
              key={link.path}
              to={link.path}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 16px',
                borderRadius: '6px',
                textDecoration: 'none',
                fontSize: '0.9rem',
                fontWeight: 600,
                color: isActive ? 'var(--text-main)' : 'var(--text-muted)',
                backgroundColor: isActive ? 'rgba(56, 139, 253, 0.15)' : 'transparent',
                border: isActive ? '1px solid rgba(56, 139, 253, 0.3)' : '1px solid transparent',
                transition: 'all 0.2s cubic-bezier(0.16, 1, 0.3, 1)'
              }}
            >
              <Icon size={16} />
              <span>{link.label}</span>
            </Link>
          );
        })}
      </div>

      {/* Network Status Badge */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          backgroundColor: 'var(--color-success)',
          boxShadow: '0 0 10px var(--color-success)'
        }} />
        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>
          SECURE
        </span>
      </div>
    </nav>
  );
}
