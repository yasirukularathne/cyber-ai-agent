# Quick Start Guide - Cyber AI Agent

## ⚡ 5-Minute Setup

### 1. Install Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

### 2. Configure API Keys
Edit `backend/.env`:
```env
# Option A: Groq (FREE - Recommended)
GROQ_API_KEY=gsk_xxxxxxxxxxxxx  # Get free key from groq.com
USE_GROQ=true

# Option B: OpenAI (PAID)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
USE_GROQ=false
```

### 3. Run Tests
```bash
cd backend
pytest tests/ -v
# Expected: 18 passed ✅
```

### 4. Start Servers
**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate  # Windows: venv\Scripts\activate (or . venv/bin/activate on Unix)
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Access: http://localhost:5173
```

### 5. Test Workflow
1. Go to http://localhost:5173/upload
2. Upload a CSV file with required columns (see below)
3. Click "Analyze"
4. View results on Dashboard/Threats/Reports/Debug

---

## 📋 CSV Format Requirements

Your CSV must have these 18 columns (exact names, whitespace stripped):

```
Flow Duration
Total Fwd Packets
Total Backward Packets
Total Length of Fwd Packets
Total Length of Bwd Packets
Flow Bytes/s
Flow Packets/s
Fwd Packet Length Mean
Bwd Packet Length Mean
Flow IAT Mean
Fwd IAT Mean
Bwd IAT Mean
Fwd PSH Flags
Bwd PSH Flags
Fwd URG Flags
Bwd URG Flags
Destination Port
Average Packet Size
```

**Optional:** Source IP column (auto-generated if missing)

---

## 🔗 Important URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:5173 | Main React app |
| Backend API | http://localhost:8000 | FastAPI server |
| API Docs | http://localhost:8000/docs | Swagger interactive docs |
| API Redoc | http://localhost:8000/redoc | API reference |

---

## 🧪 Verify Each Component

### Backend Startup Check
```bash
curl http://localhost:8000/
# Expected: {"status": "Cyber AI Agent v2 running", "docs": "/docs"}
```

### Test API Endpoint
```bash
curl -X POST http://localhost:8000/api/upload-logs \
  -F "file=@your_data.csv"
```

### Check Latest Debug Output
```bash
curl http://localhost:8000/api/debug/latest | jq
# Returns full 8-layer execution trace
```

---

## 📂 Project Structure Quick Reference

```
cyber-ai-agent/
├── backend/
│   ├── app/
│   │   ├── main.py              ← FastAPI entry point
│   │   ├── pipeline.py          ← 8-layer orchestrator
│   │   ├── layers/              ← All 8 pipeline layers
│   │   ├── routes/              ← API endpoints
│   │   ├── models/              ← Pydantic schemas
│   │   └── utils/               ← Logger
│   ├── tests/                   ← 18 unit tests
│   ├── trained_models/          ← Pre-trained models
│   ├── debug_logs/              ← Auto-created debug output
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/               ← 5 React pages
│   │   ├── components/          ← Shared components
│   │   ├── App.jsx              ← Router
│   │   └── index.css            ← Styling
│   └── package.json
└── IMPLEMENTATION_CHECKLIST.md  ← Full documentation
```

---

## 🐛 Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: groq` | Dependencies not installed | Run `pip install -r requirements.txt` |
| API key error in reports | Missing GROQ_API_KEY/.env | Set API key in `backend/.env` |
| CORS error | Frontend/backend mismatch | Ensure backend on :8000, frontend on :5173 |
| CSV validation error | Missing columns | Check column names match exactly |
| "Model not found" | Wrong working directory | Run from `backend/` folder |
| Port already in use | Another app using port | Change port: `--port 8001` |

---

## 📊 Pipeline Layers Explained

```
Input CSV
    ↓
L1: Ingestion       → Parse CSV, validate columns, extract IPs
    ↓
L2: Preprocessing   → Scale features, generate NLP descriptions
    ↓
L3: XGBoost         → Multi-class threat classification (0-4 labels)
L4: BERT            → NLP-based threat classification
L5: Autoencoder     → Anomaly detection via reconstruction error
    ↓
L6: Fusion          → Weighted ensemble: 40% XGBoost + 40% BERT + 20% AE
    ↓
L7: MCP Tools       → Enrich with IP reputation, CVE lookups
    ↓
L8: LLM Explainer   → Generate human-readable explanations (Groq/OpenAI)
    ↓
Output: Threats with explanations, severity, and mitigation steps
```

---

## ✅ Validation Checklist

Run these commands to verify everything works:

```bash
# 1. Test Python environment
python --version  # Should be 3.9+
pip list | grep fastapi

# 2. Test models exist
ls backend/trained_models/
# Should show: xgboost_model.pkl, autoencoder.keras, bert_classifier/, etc.

# 3. Run all unit tests
cd backend && pytest tests/ -v  # Should show 18 passed ✅

# 4. Check FastAPI is running
curl http://localhost:8000/  # Should get {"status": "Cyber AI Agent v2 running"}

# 5. Check React can reach backend
curl http://localhost:8000/api/debug/latest  # Should return JSON

# 6. Frontend loads
# Open http://localhost:5173 in browser - should see Navbar + Dashboard
```

---

## 🚀 Test the Full Pipeline

1. **Prepare test data**: Save as `sample.csv` in UTF-8
   ```
   Flow Duration,Total Fwd Packets,Total Backward Packets,...
   120,10,5,300,150,100.5,25.3,30.0,30.0,5.0,3.0,4.0,0,0,0,0,80,20.0
   ```

2. **Upload via API**:
   ```bash
   curl -X POST http://localhost:8000/api/upload-logs \
     -F "file=@sample.csv"
   # Response: {"filename": "sample.csv", "status": "uploaded"}
   ```

3. **Run prediction**:
   ```bash
   curl -X POST "http://localhost:8000/api/predict?filename=sample.csv&debug=true"
   # Response: Full pipeline output with all 8 layers + threats
   ```

4. **View in browser**:
   - Upload UI: http://localhost:5173/upload
   - View threats: http://localhost:5173/threats
   - View debug: http://localhost:5173/debug
   - View explanations: http://localhost:5173/reports

---

## 📚 Additional Resources

- **Implementation Details**: See `IMPLEMENTATION_CHECKLIST.md` in project root
- **Layer Specifications**: Check individual files in `backend/app/layers/`
- **Test Examples**: See `backend/tests/` folder for each layer's tests
- **API Docs**: http://localhost:8000/docs (when backend is running)

---

## 🎓 Understanding Debug Output

The debug endpoint returns full layer-by-layer execution:

```json
{
  "run_id": "20260527_143022",
  "layers": {
    "ingestion": {
      "status": "OK",
      "row_count": 100,
      "columns": [...],
      "ips": [...]
    },
    "preprocessing": {
      "status": "OK",
      "null_count_after_clean": 0,
      "scaled_features": "<ndarray shape=(100, 18)>"
    },
    "xgboost": {
      "status": "OK",
      "predictions": [{label: 0, confidence: 0.95}],
      "attack_count": 0
    },
    ...
    "llm": {
      "status": "OK",
      "explained_threats": [{
        "explanation": "...",
        "why_dangerous": "...",
        "mitigation": ["1...", "2...", "3..."],
        "severity": "HIGH"
      }]
    }
  }
}
```

Each layer is independently verifiable!

---

## 💡 Next Steps After Setup

1. ✅ Run tests: `pytest tests/ -v`
2. ✅ Start servers (2 terminals)
3. ✅ Upload sample CSV
4. ✅ Check Debug View for layer outputs
5. ✅ Review Reports for LLM explanations
6. 📈 Prepare real dataset for retraining (optional, for production)
7. 🔐 Add authentication before deployment (recommended)

---

**Status:** Ready for Development & Testing  
**Version:** 2.0.0  
**Last Updated:** May 27, 2026
