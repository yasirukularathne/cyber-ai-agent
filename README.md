# Cyber AI Agent

Cyber AI Agent is a full-stack network intrusion detection system built for the Advanced Artificial Intelligence group project. It analyzes network-flow CSV files with an 8-layer AI pipeline, then presents detections, model outputs, debug traces, and analyst-style explanations in a React dashboard.

The project fits the telecommunications / cybersecurity domain from the assignment brief and demonstrates more than the required minimum of three Advanced AI techniques: NLP text generation, transformer transfer learning, unsupervised autoencoder anomaly detection, ensemble fusion, and prompt-engineered LLM explanations.

## Quick Start

Use this when the dependencies and trained model artifacts are already available in the workspace.

```powershell
# Terminal 1: backend
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000

# Terminal 2: frontend
cd frontend
npm install
npm run dev
```

Open:

- Frontend: http://localhost:3000
- Backend health check: http://localhost:8000
- API documentation: http://localhost:8000/docs

For a fresh machine setup, see [SETUP.md](SETUP.md). That guide creates a new `.venv`; this workspace also has a populated `backend\venv`.

## What It Does

- Uploads CIC-style network flow CSV files.
- Validates and aligns 18 required numeric traffic features.
- Converts each flow into a natural-language description for transformer inference.
- Runs XGBoost, BERT, and an autoencoder over the same records.
- Fuses supervised and unsupervised model signals into threat decisions.
- Enriches detections with rule-based threat intelligence.
- Generates human-readable explanations and mitigation guidance through Groq when configured, or mock explanations when no key is present.
- Shows results through Dashboard, Upload, Threats, Reports, Debug, and model-check pages.

## AI Techniques Used

| Assignment technique         | Project implementation                                                                                            |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Natural Language Processing  | `PreprocessingLayer` converts numeric flow records into semantic network-flow text.                               |
| Transformer-based Models     | `BERTLayer` uses a fine-tuned `prajjwal1/bert-tiny` classifier for attack classification from generated text.     |
| Generative AI / Autoencoders | `AutoencoderLayer` uses reconstruction error to detect anomalous flows learned from benign traffic.               |
| Transfer Learning            | BERT starts from a pretrained transformer and is adapted to network attack classes.                               |
| Ensemble Methods             | `FusionLayer` combines XGBoost, BERT, and autoencoder outputs with weighted confidence scoring.                   |
| Prompt Engineering           | `LLMExplainerLayer` prompts a cybersecurity analyst model to return structured JSON explanations and mitigations. |

## Architecture

```text
CSV network flow log
        |
        v
Layer 1: Ingestion
  - Parse CSV
  - Validate required columns
  - Extract source IPs when available
        |
        v
Layer 2: Preprocessing
  - Clean numeric features
  - Scale values
  - Generate NLP text per flow
        |
        v
Layers 3-5: Model inference
  - XGBoost supervised classifier
  - BERT transformer classifier
  - Autoencoder anomaly detector
        |
        v
Layer 6: Fusion
  - Resolve attack class
  - Combine confidence signals
  - Assign severity
        |
        v
Layer 7: MCP / threat intelligence tools
  - Add enrichment fields
        |
        v
Layer 8: LLM explainer
  - Produce analyst explanation
  - Provide mitigation guidance
        |
        v
React dashboard + JSON API response
```

## Tech Stack

| Area              | Tools                                                          |
| ----------------- | -------------------------------------------------------------- |
| Backend API       | Python, FastAPI, Uvicorn, Pydantic                             |
| Machine learning  | scikit-learn, XGBoost, TensorFlow/Keras, PyTorch, Transformers |
| LLM integration   | Groq API with mock fallback                                    |
| Frontend          | React 18, Vite, React Router, Axios, Recharts, Lucide React    |
| Testing           | Pytest                                                         |
| Research workflow | Jupyter notebooks                                              |

## Repository Structure

```text
cyber-ai-agent/
  backend/
    app/
      main.py                  FastAPI application entry point
      pipeline.py              8-layer pipeline orchestrator
      layers/                  ingestion, preprocessing, models, fusion, enrichment, LLM
      routes/                  upload, predict, dashboard, reports, debug APIs
      models/                  Pydantic schemas
      utils/                   logging helpers
    datasets/                  local CIC-IDS style datasets and splits
    notebooks/                 training and experiment notebooks
    tests/                     layer-level pytest suite
    trained_models/            local model artifacts and metrics
    init_models.py             lightweight model initializer for fresh demos
    requirements.txt           Python dependencies
  frontend/
    src/
      components/              reusable UI components
      pages/                   dashboard, upload, threats, reports, debug, model checks
      utils/                   shared label helpers
    package.json               frontend dependencies and scripts
    vite.config.js             Vite dev server config, port 3000
  reports/
    cyber_ai_agent_report.pdf  compiled project report
    cyber_ai_agent_report.tex  LaTeX report source
  CODE_REVIEW.md
  README.md
  SETUP.md
```

## Dataset Format

The uploaded CSV must contain these 18 columns. Extra columns are allowed; source IP columns are optional.

```csv
Flow Duration,Total Fwd Packets,Total Backward Packets,Total Length of Fwd Packets,Total Length of Bwd Packets,Flow Bytes/s,Flow Packets/s,Fwd Packet Length Mean,Bwd Packet Length Mean,Flow IAT Mean,Fwd IAT Mean,Bwd IAT Mean,Fwd PSH Flags,Bwd PSH Flags,Fwd URG Flags,Bwd URG Flags,Destination Port,Average Packet Size
45000,120,45,8500,2100,1892.31,3.67,70.83,46.67,375.25,30.1,27.5,1,0,0,0,443,58.5
```

Optional IP column names recognized by ingestion:

- `Source IP`
- `Src IP`
- `src_ip`
- `Source_IP`
- `src`

If no source IP column exists, the pipeline uses `unknown` placeholders so CIC flow exports still run.

## API Endpoints

| Method | Endpoint                                  | Purpose                                                       |
| ------ | ----------------------------------------- | ------------------------------------------------------------- |
| `GET`  | `/`                                       | Backend health check.                                         |
| `POST` | `/api/upload-logs`                        | Upload a CSV file.                                            |
| `POST` | `/api/predict?filename=<file>&debug=true` | Run the full 8-layer detection pipeline.                      |
| `GET`  | `/api/dashboard`                          | Return summary counts and recent threats from the latest run. |
| `GET`  | `/api/reports`                            | Return LLM explanation reports from the latest run.           |
| `GET`  | `/api/debug/runs`                         | List saved debug run IDs.                                     |
| `GET`  | `/api/debug/run/{run_id}`                 | Read a specific debug run.                                    |
| `GET`  | `/api/debug/latest`                       | Read the latest debug run.                                    |

## Frontend Pages

| Route                | Page                                               |
| -------------------- | -------------------------------------------------- |
| `/`                  | Dashboard summary and model breakdown.             |
| `/upload`            | CSV upload and analysis trigger.                   |
| `/threats`           | Threat table with severity and model signals.      |
| `/reports`           | AI-generated explanations and mitigation guidance. |
| `/debug`             | Layer-by-layer pipeline debug output.              |
| `/xgboost-check`     | XGBoost inspection page.                           |
| `/bert-check`        | BERT inspection page.                              |
| `/autoencoder-check` | Autoencoder inspection page.                       |

## Configuration

Create `backend/.env` from `backend/.env.example`:

```powershell
cd backend
Copy-Item .env.example .env
```

LLM explanations work without an API key. When `GROQ_API_KEY` is blank or set to a placeholder, the backend uses deterministic mock explanations suitable for local demos.

```env
GROQ_API_KEY=
GROQ_MODEL=openai/gpt-oss-120b
```

## Model Artifacts

The runtime expects these model files under `backend/trained_models/`:

- `scaler.pkl`
- `feature_names.json`
- `xgboost_model.pkl`
- `autoencoder.keras`
- `autoencoder_threshold.json`
- `bert_classifier/`
- `label_map.json`

These artifacts are intentionally ignored by git because they can be large. For the final demo, keep the trained artifacts in the workspace or provide them with the submission package. For a lightweight smoke-test setup, run:

```powershell
cd backend
python init_models.py
```

`init_models.py` creates small placeholder artifacts for local execution. Use the real trained artifacts and notebooks for final reported results.

## Saved Evaluation Snapshot

Current saved metrics under `backend/trained_models/` include:

| Component         | Metric snapshot                                                   |
| ----------------- | ----------------------------------------------------------------- |
| XGBoost           | Accuracy `0.9974`, F1 `0.9969`, 15 classes, 18 features.          |
| BERT              | Accuracy `0.9513`, F1 `0.9465`, base model `prajjwal1/bert-tiny`. |
| Autoencoder       | Accuracy `0.8853`, F1 `0.6329`, false positive rate `0.0494`.     |
| Fusion experiment | Accuracy `0.9750`, F1 `0.9713`.                                   |

The current implementation-level fusion weights are defined in `backend/app/layers/fusion.py`.

## Tests

Run the backend tests from the backend directory:

```powershell
cd backend
python -m pytest tests -v
```

The test suite covers ingestion, preprocessing, XGBoost, BERT, autoencoder, fusion, MCP enrichment, and LLM explanation behavior.

## Reproducibility Notes

- Use Python 3.11 for the existing local virtual environments, or Python 3.9+ if creating a fresh one.
- Use Node.js 18+ for the Vite frontend.
- Run backend commands from `backend/` so relative paths such as `trained_models/` resolve correctly.
- Keep `backend/.env` private. Commit `backend/.env.example` only.
- Keep notebooks documented with markdown cells for the final assignment requirement.
- Keep final metrics synchronized with the JSON artifacts and the report.

## Troubleshooting

| Problem                          | Fix                                                                                             |
| -------------------------------- | ----------------------------------------------------------------------------------------------- |
| `ModuleNotFoundError` in backend | Activate the backend virtual environment and reinstall `requirements.txt`.                      |
| Backend cannot find models       | Confirm `backend/trained_models/` exists, or run `python init_models.py` for demo placeholders. |
| Frontend shows no data           | Upload a CSV, run prediction, then refresh Dashboard/Threats/Reports.                           |
| API calls fail from frontend     | Confirm backend is running on `http://localhost:8000`.                                          |
| Frontend port confusion          | This project uses Vite port `3000`, configured in `frontend/vite.config.js`.                    |
| CSV validation fails             | Match the 18 required feature column names exactly; extra columns are fine.                     |
| LLM reports say mock/fallback    | Add a real `GROQ_API_KEY` to `backend/.env`, or keep mock mode for demos.                       |

## Assignment Deliverables

The course document asks for:

- Final report, maximum 20 pages excluding references and appendices.
- Demonstrable output, either research findings or a functional AI product.
- Associated Python code and notebooks that are documented and reproducible.
- README with setup instructions and dependencies.
- Video presentation, maximum 5 minutes.
- APA 7th edition references.

Current project assets already include a functional product, backend tests, training notebooks, this README/setup guide, and a compiled report under `reports/`.

## License

Educational project for the Advanced Artificial Intelligence group assignment.
