import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import LogUpload from './pages/LogUpload';
import Threats from './pages/Threats';
import Reports from './pages/Reports';
import DebugView from './pages/DebugView';
import XGBoostCheck from './pages/XGBoostCheck';
import BERTCheck from './pages/BERTCheck';
import AutoencoderCheck from './pages/AutoencoderCheck';

export default function App() {
  return (
    <Router>
      <div style={{ 
        backgroundColor: 'var(--bg-primary)', 
        minHeight: '100vh', 
        color: 'var(--text-main)', 
        display: 'flex', 
        flexDirection: 'column' 
      }}>
        <Navbar />
        <main style={{ 
          flex: 1, 
          padding: '32px 24px', 
          maxWidth: '1400px', 
          width: '100%', 
          margin: '0 auto',
          boxSizing: 'border-box'
        }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<LogUpload />} />
            <Route path="/threats" element={<Threats />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/debug" element={<DebugView />} />
            <Route path="/xgboost-check" element={<XGBoostCheck />} />
            <Route path="/bert-check" element={<BERTCheck />} />
            <Route path="/autoencoder-check" element={<AutoencoderCheck />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
