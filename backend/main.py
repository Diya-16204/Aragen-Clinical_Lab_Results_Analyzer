from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agent.lab_agent import AIServiceError, UnknownLabError, analyze_labs, tool_payload
from models.schemas import AnalyzeRequest, AnalyzeResponse, AskAragenDocRequest, AskAragenDocResponse
from mcp_server.server import mcp
from reference_ranges import REFERENCE_RANGES

# The project .env is the local runtime configuration source of truth.
load_dotenv(Path(__file__).with_name(".env"), override=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(title="Clinical Lab Results Analyzer API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    # Vite selects the next available local port when 5173 is occupied.
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+$",
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/reference_ranges")
async def reference_ranges():
    """Return supported deterministic ranges for the UI glossary."""
    unique = {item.canonical_name: item for item in REFERENCE_RANGES.values()}
    return {"tests": [{"test_name": item.canonical_name, "unit": item.unit, "reference_range": item.display_range,
                       "normal": [item.normal_low, item.normal_high], "warning": [item.warning_low, item.warning_high],
                       "critical": [item.critical_low, item.critical_high]} for item in sorted(unique.values(), key=lambda value: value.canonical_name)]}


@app.post("/analyze_labs", response_model=AnalyzeResponse)
async def analyze_labs_endpoint(request: AnalyzeRequest):
    try:
        results, activity, overall_summary = await analyze_labs([item.model_dump() for item in request.labs], request.language)
        return {"results": results, "agent_activity": activity, "overall_summary": overall_summary}
    except UnknownLabError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except AIServiceError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@app.post("/ask_aragen_doc", response_model=AskAragenDocResponse)
async def ask_aragen_doc_endpoint(request: AskAragenDocRequest):
    response = await mcp.call_tool("ask_aragen_doc", {"question": request.question, "lab_results": [item.model_dump() for item in request.lab_results], "language": request.language})
    payload = tool_payload(response)
    activity = {"tool": "ask_aragen_doc", "status": "completed" if payload["ok"] else "failed", "details": f"Question: {request.question}"}
    if not payload["ok"]:
        raise HTTPException(status_code=503, detail={"message": payload["error"], "agent_activity": activity})
    return {"answer": payload["answer"], "suggested_specialist": payload["suggested_specialist"], "safety_note": payload["safety_note"], "agent_activity": activity}
