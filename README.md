# Clinical Lab Results Analyzer

A hackathon-ready clinical decision-support MVP that turns manual or CSV lab entries into transparent **NORMAL**, **WARNING**, and **CRITICAL** findings. It is not a diagnostic device.

## Architecture

```text
React dashboard → FastAPI /analyze_labs → Lab Agent
                                         ├─ MCP deterministic tools: CLASSIFY
                                         ├─ severity routing: CRITICAL → WARNING → NORMAL
                                         └─ MCP explain tool → Gemini: EXPLAIN only
```

The Python MCP server lives in `backend/mcp_server/server.py`. It publishes `reference_range_lookup`, `classify_lab_result`, and `explain_lab_result` tools. The FastAPI agent dispatches both classification and Gemini explanation through FastMCP's registered tools, and the same tools are exposed over stdio to any MCP-capable client. MCP is therefore an executable part of the agent workflow, not a display-only layer.

## Classification

Supported demo labs are Hemoglobin, Glucose, WBC, Platelets, Creatinine, Sodium, Potassium, Cholesterol, and Bilirubin. Each has fixed normal, warning, and critical bounds in `backend/reference_ranges.py`. The agent evaluates critical bounds first, then warning, then normal. Units must match the supported unit. These adult-oriented demo intervals are intentionally transparent and should not be used as patient-specific guidance.

## Run

Use two terminals from the project root.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn main:app --reload --port 8000
```

Add a live LLM provider before analysing results. The assignment requires a real LLM call for every explanation, so the API returns a clear configuration error until a valid key is present. Set `AI_PROVIDER=groq` and `GROQ_API_KEY=your_key` (default model: `openai/gpt-oss-20b`), or set `AI_PROVIDER=gemini` and `GEMINI_API_KEY=your_key` (default: `gemini-3.6-flash`). The LLM is only given the already-fixed result plus reference range and is instructed to return JSON with clinical context and a next step; it can never set the classification.

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL, normally `http://localhost:5173`.

The dashboard/API already dispatches classification through the registered MCP tool interface; **do not run the MCP server directly in an ordinary PowerShell terminal**, because its standard input/output are reserved for JSON-RPC messages from an MCP client. To connect it to an MCP-capable client, use this configuration:

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

## API example

```powershell
Invoke-RestMethod -Method Post http://localhost:8000/analyze_labs -ContentType 'application/json' -Body '{"labs":[{"test_name":"Hemoglobin","value":8.5,"unit":"g/dL"},{"test_name":"Glucose","value":180,"unit":"mg/dL"}]}'
```

## Demo flow

1. Start both servers and open the dashboard.
2. Use the preloaded Hemoglobin, Glucose, and Potassium values, or upload `test_data/critical.csv`.
3. Select **Analyze results**.
4. Show critical entries sorted first, then their clinical context and suggested next step.
5. Point out the visible reference ranges and explain: fixed MCP classification first; Gemini explanation second.

`test_data/normal.csv`, `warning.csv`, and `critical.csv` are clearly-labelled synthetic development fixtures. Before submitting, download the required Kaggle Laboratory Test Results - Anonymized Dataset, preserve it in `test_data/kaggle_laboratory_results.csv`, and document any column mapping. See `test_data/README.md`.

## Project phases

**Phase 1 is complete:** the current MVP implements the end-to-end assignment workflow. Planned enhancements, including trend history, exports, a severity chart, a reference glossary, automated tests, and GitHub delivery, are documented in `PHASES.md` as Phase 2 work.
