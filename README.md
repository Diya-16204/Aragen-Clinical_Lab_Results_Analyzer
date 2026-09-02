# ✚ Clinical Lab Results Analyzer

> A transparent, AI-assisted clinical decision-support MVP for reviewing laboratory values — built for hackathon demonstration and educational use.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-137C68?style=for-the-badge)](https://aragen-clinical-lab-results-analyze.vercel.app/)
[![API Health](https://img.shields.io/badge/API-Render-4C8BF5?style=for-the-badge)](https://aragen-clinical-lab-results-analyzer.onrender.com/health)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge)](https://react.dev/)

## 🌐 Live links

| Service | URL |
| --- | --- |
| Dashboard | [aragen-clinical-lab-results-analyze.vercel.app](https://aragen-clinical-lab-results-analyze.vercel.app/) |
| Backend API | [aragen-clinical-lab-results-analyzer.onrender.com](https://aragen-clinical-lab-results-analyzer.onrender.com) |
| API health check | [/health](https://aragen-clinical-lab-results-analyzer.onrender.com/health) |
| Interactive API docs | [/docs](https://aragen-clinical-lab-results-analyzer.onrender.com/docs) |

## ✨ What it does

Clinical Lab Results Analyzer accepts laboratory values through a manual form or CSV upload, evaluates them against fixed demo reference ranges, then prioritizes findings and uses an LLM only to add explanatory context.

The key design choice is intentional: **the LLM never determines the clinical status.** Classification is deterministic, explainable, and visible in the UI.

## 🚀 Key features

- Manual laboratory entry with add/remove rows.
- CSV upload with row-range selection and Kaggle-style column mapping.
- Deterministic `NORMAL`, `WARNING`, and `CRITICAL` classification.
- Nine supported test types: Hemoglobin, Glucose, WBC, Platelets, Creatinine, Sodium, Potassium, Cholesterol, and Bilirubin.
- Reference-range explainability, high/low direction, and deterministic classification reasons.
- Groq-powered individual explanations and overall AI analysis summary.
- Ask Aragen Doc: constrained question-and-answer using current analyzed results.
- English and Hindi AI-generated explanations with live switching.
- Actual MCP Activity trace for the backend tool workflow.
- Visual analytics, severity summaries, range visualizations, and dated trend history.
- CSV export, Print / Save PDF, reference glossary, and demo presets.

## 🧭 Product flow

```text
Manual entry / CSV upload
          │
          ▼
 FastAPI /analyze_labs
          │
          ├── MCP: reference_range_lookup
          ├── MCP: classify_lab_result       ← deterministic rules
          ├── Severity routing               ← CRITICAL → WARNING → NORMAL
          ├── MCP: explain_lab_result        ← Groq explanation only
          └── MCP: generate_overall_summary  ← Groq synthesis only
          │
          ▼
 React dashboard: findings, charts, exports, Ask Aragen Doc
```

## 🧱 Architecture

| Layer | Technology | Responsibility |
| --- | --- | --- |
| Frontend | React + Vite | Entry forms, CSV workflow, dashboard, exports, language switching |
| API | FastAPI + Pydantic | Validation, CORS, endpoints, deployment-ready backend |
| Agent | Python | Classify → route → explain orchestration |
| MCP | FastMCP | Real reference, classification, explanation, summary, and Aragen Doc tools |
| AI | Groq | Explanatory text and summaries after classification |
| Hosting | Vercel + Render | Static dashboard and FastAPI service |

## 🔎 Deterministic classification

Reference ranges live in [`backend/reference_ranges.py`](backend/reference_ranges.py). The app validates the unit, looks up its fixed range, assigns the status, and sorts results by urgency.

| Status | Meaning in this demo |
| --- | --- |
| `CRITICAL` | Far outside the configured demo boundary; displayed first |
| `WARNING` | Outside the normal interval but not in the configured critical boundary |
| `NORMAL` | Within the configured demo reference interval |

These are transparent, adult-oriented **demo defaults**, not patient-specific laboratory interpretation.

## 🤖 AI and safety boundaries

Groq receives already-classified results and is used to explain, not decide.

- Values, units, ranges, statuses, ordering, and chart data are deterministic.
- Every result displays its source range and classification reason.
- Ask Aragen Doc is informational and uses current results as context.
- Medication, dosage, prescription, and classification-change requests are safely refused.
- This application is **not a diagnostic device** and does not replace qualified clinical judgment.

## 🗣️ Languages

The dashboard header supports:

- **English** — default.
- **हिंदी** — simple Devanagari Hindi for AI explanations, overall summary, and Ask Aragen Doc.

Changing language reuses the entered values and refreshes AI content. It never changes values, units, reference ranges, statuses, labels, or charts.

## 📁 Repository structure

```text
Aragen/
├── backend/
│   ├── agent/              # CLASSIFY → ROUTE → EXPLAIN orchestration
│   ├── mcp_server/         # Registered FastMCP tools
│   ├── models/             # Pydantic request/response schemas
│   ├── services/           # Groq/Gemini provider integration
│   ├── tests/              # Deterministic and safety tests
│   ├── main.py             # FastAPI application and CORS configuration
│   ├── reference_ranges.py # Fixed demo ranges
│   └── requirements.txt
├── frontend/src/           # React dashboard and components
├── test_data/              # Synthetic and Kaggle-style CSV fixtures
├── render.yaml             # Render deployment definition
└── README.md
```

## 🛠️ Run locally

### Prerequisites

- Python 3.11+ (3.12 recommended)
- Node.js 18+
- A Groq API key

### 1. Start the backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set these values in `backend/.env`:

```env
AI_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

Then run:

```powershell
uvicorn main:app --reload --port 8000
```

API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the displayed Vite URL, normally [http://localhost:5173](http://localhost:5173).

## 🔌 API reference

### `POST /analyze_labs`

Classifies lab values deterministically and generates AI explanation content.

```json
{
  "labs": [
    { "test_name": "Hemoglobin", "value": 8.5, "unit": "g/dL" },
    { "test_name": "Glucose", "value": 180, "unit": "mg/dL" }
  ],
  "language": "en"
}
```

`language` is optional and accepts `en` or `hi`; it defaults to `en`.

### `POST /ask_aragen_doc`

Sends a constrained informational question about the current analysis.

```json
{
  "question": "Why is my hemoglobin flagged?",
  "lab_results": ["<current results from /analyze_labs>"],
  "language": "en"
}
```

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Deployment health check |
| `GET /reference_ranges` | Supported tests and configured demo ranges |
| `GET /docs` | FastAPI Swagger UI |

## 🧪 Test data and demo script

Included fixtures in [`test_data`](test_data):

- `normal.csv`
- `warning.csv`
- `critical.csv`
- `kaggle_laboratory_results.csv`

Suggested two-minute demo:

1. Open the [live dashboard](https://aragen-clinical-lab-results-analyze.vercel.app/).
2. Click **Mixed severity**, then **Analyze results**.
3. Show the deterministic reason, reference range, direction, and priority order.
4. Expand **MCP Activity** to show the actual tool path.
5. Show the AI summary, visual analytics, and CSV/PDF export controls.
6. Switch to **हिंदी** to demonstrate refreshed AI content while classifications remain fixed.
7. Ask Aragen Doc: “Why is my hemoglobin flagged?”

## ✅ Testing

Run backend tests:

```powershell
cd backend
python -m unittest discover -s tests -v
```

Build the production frontend:

```powershell
cd frontend
npm run build
```

Tests cover deterministic normal, warning, critical, invalid-unit, unknown-test, and Ask Aragen Doc medication-safety cases.

## 🚢 Deployment

```text
Vercel React dashboard
        │ HTTPS + VITE_API_URL
        ▼
Render FastAPI service
        │
        ▼
Groq API
```

### Render backend

- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Health check: `/health`

Required environment variables:

```env
AI_PROVIDER=groq
GROQ_API_KEY=your_secret_key
GROQ_MODEL=openai/gpt-oss-20b
FRONTEND_ORIGIN=https://aragen-clinical-lab-results-analyze.vercel.app
```

### Vercel frontend

- Root directory: `frontend`
- Framework: Vite

```env
VITE_API_URL=https://aragen-clinical-lab-results-analyzer.onrender.com
```

Never commit API keys. `backend/.env` is excluded by `.gitignore`.

## MCP client connection (optional)

The dashboard already invokes registered MCP tools inside the backend. Do **not** run the MCP server in a regular terminal because stdio is reserved for JSON-RPC communication.

To connect an MCP-capable client locally:

```json
{
  "mcpServers": {
    "clinical-lab-analyzer": {
      "command": "C:\\Users\\Sach\\Downloads\\SHAMBHU\\Projects\\Aragen\\backend\\.venv\\Scripts\\python.exe",
      "args": ["-m", "mcp_server.server"],
      "cwd": "C:\\Users\\Sach\\Downloads\\SHAMBHU\\Projects\\Aragen\\backend"
    }
  }
}
```

## ⚠️ Disclaimer

This is an educational hackathon prototype for transparent clinical decision support. It does not diagnose conditions, prescribe treatment, replace laboratory-specific reference intervals, or replace consultation with a qualified healthcare professional. If a result may be urgent, seek appropriate professional care.

---

Built with React, FastAPI, FastMCP, Groq, Vercel, and Render.
