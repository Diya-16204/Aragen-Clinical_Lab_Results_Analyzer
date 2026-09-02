"""CLASSIFY → ROUTE → EXPLAIN orchestration via the registered MCP tools."""
import json
from mcp_server.server import mcp

ORDER = {"CRITICAL": 0, "WARNING": 1, "NORMAL": 2}


class UnknownLabError(ValueError):
    pass


class AIServiceError(RuntimeError):
    pass


def classification_reason(result: dict) -> str:
    if result["status"] == "NORMAL":
        return f"{result['value']} {result['unit']} is within the fixed demo reference range of {result['reference_range']}."
    if result["value"] < result["normal_low"]:
        delta = result["normal_low"] - result["value"]
        return f"{result['value']} {result['unit']} is {delta:g} {result['unit']} below the lower reference limit of {result['normal_low']:g}; deterministic rules assign {result['status']}."
    delta = result["value"] - result["normal_high"]
    return f"{result['value']} {result['unit']} is {delta:g} {result['unit']} above the upper reference limit of {result['normal_high']:g}; deterministic rules assign {result['status']}."


def direction(result: dict) -> str:
    if result["value"] < result["normal_low"]:
        return "LOW"
    if result["value"] > result["normal_high"]:
        return "HIGH"
    return "IN RANGE"


def tool_payload(response: object) -> dict:
    return response if isinstance(response, dict) else json.loads(response[0].text)


async def analyze_labs(labs: list[dict]) -> tuple[list[dict], list[dict]]:
    classified = []
    activity = []
    for lab in labs:
        lookup_response = await mcp.call_tool("reference_range_lookup", {"test_name": lab["test_name"]})
        lookup = tool_payload(lookup_response)
        if not lookup["found"]:
            raise UnknownLabError(lookup["message"])
        activity.append({"tool": "reference_range_lookup", "status": "completed", "details": f"{lookup['test_name']} → {lookup['reference_range']}"})
        # Dispatch through FastMCP's actual registered tool interface. The same
        # tools are exposed over stdio when `python -m mcp_server.server` runs.
        response = await mcp.call_tool("classify_lab_result", lab)
        tool_result = tool_payload(response)
        if not tool_result["found"]:
            raise UnknownLabError(tool_result["message"])
        tool_result["classification_reason"] = classification_reason(tool_result)
        tool_result["direction"] = direction(tool_result)
        tool_result["date"] = lab.get("date")
        classified.append(tool_result)
        activity.append({"tool": "classify_lab_result", "status": "completed", "details": f"{tool_result['test_name']} {tool_result['value']} {tool_result['unit']} → {tool_result['status']}"})
    classified.sort(key=lambda item: ORDER[item["status"]])  # ROUTE
    activity.append({"tool": "severity_routing", "status": "completed", "details": "Results sorted: Critical → Warning → Normal"})
    for result in classified:  # EXPLAIN through MCP; classification is already fixed
        response = await mcp.call_tool("explain_lab_result", result)
        explanation_result = tool_payload(response)
        if not explanation_result["ok"]:
            result["explanation"] = "Live LLM clinical context is temporarily unavailable. The deterministic classification and reference range remain valid decision-support information."
            result["next_step"] = "Review this result using local clinical protocols and retry the AI explanation when the provider is available."
            activity.append({"tool": "explain_lab_result", "status": "failed", "details": f"{result['test_name']}: {explanation_result['error']}"})
            continue
        result["explanation"] = explanation_result["explanation"]
        result["next_step"] = explanation_result["next_step"]
        activity.append({"tool": "explain_lab_result", "status": "completed", "details": f"{result['test_name']}: Groq LLM explanation generated"})
    return classified, activity
