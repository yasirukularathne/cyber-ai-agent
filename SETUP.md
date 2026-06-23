# Setup Guide

This guide sets up the Cyber AI Agent backend and frontend on Windows PowerShell. The same commands can be adapted for macOS or Linux by changing virtual environment activation paths.

This guide uses `.venv` for a fresh environment. The current workspace also contains `backend\venv`, which already has the backend dependencies installed.

## Prerequisites

- Python 3.9+; Python 3.11 is recommended for this workspace.
- Node.js 18+ and npm.
- At least 4 GB RAM for loading the ML stack.
- Internet access if installing dependencies or regenerating BERT artifacts.

## 1. Backend Environment

From the repository root:

```powershell
cd backend

# Create a virtual environment if one is not already available.
python -m venv .venv

# Activate it.
.\.venv\Scripts\Activate.ps1

# Install dependencies.
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation scripts, run this once for the current shell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 2. Environment Variables

Create a private backend `.env` file:

```powershell
Copy-Item .env.example .env
```

The LLM layer works in mock mode when `GROQ_API_KEY` is blank or a placeholder. Add a real key only when you want live Groq explanations.

## 3. Model Artifacts

The backend expects trained models in `backend/trained_models/`.

Required runtime files:

```text
trained_models/
  scaler.pkl
  feature_names.json
  xgboost_model.pkl
  autoencoder.keras
  autoencoder_threshold.json
  bert_classifier/
  label_map.json
```

For the final demo, use the real trained artifacts already produced by the notebooks. For a fresh local smoke test only, generate lightweight placeholders:

```powershell
python init_models.py
```

## 4. Start Backend

Run from `backend/` with the virtual environment active:

```powershell
uvicorn app.main:app --reload --port 8000
```

Check:

- Health: http://localhost:8000
- Docs: http://localhost:8000/docs

## 5. Frontend Setup

Open a second terminal from the repository root:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

## 6. Run Tests

Run backend tests:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest tests -v
```

Run a frontend production build check:

```powershell
cd frontend
npm run build
```

## 7. Demo Workflow

1. Start the backend on port `8000`.
2. Start the frontend on port `3000`.
3. Open http://localhost:3000/upload.
4. Upload a CSV with the 18 required flow features.
5. Run analysis.
6. Review:
   - Dashboard for counts and severity distribution.
   - Threats for model-level detection details.
   - Reports for LLM or mock explanations.
   - Debug for layer-by-layer pipeline output.

## 8. Required CSV Columns

```text
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

Optional source IP columns are supported: `Source IP`, `Src IP`, `src_ip`, `Source_IP`, or `src`.

## 9. Common Fixes

| Symptom | Fix |
| --- | --- |
| `Only CSV files are accepted` | Upload a file ending in `.csv`. |
| `Missing columns` | Match the required column names exactly. |
| `File not found. Upload first` | Upload through `/api/upload-logs` before calling `/api/predict`. |
| `No debug runs yet` | Run prediction at least once. |
| TensorFlow or Torch import errors | Reinstall backend dependencies in the active virtual environment. |
| Frontend cannot connect | Confirm the backend is running at `http://localhost:8000/api`. |
| Port `3000` busy | Change `frontend/vite.config.js` or stop the process using that port. |
