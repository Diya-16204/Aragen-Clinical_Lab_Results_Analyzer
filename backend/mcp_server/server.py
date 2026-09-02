"""MCP server exposing the deterministic lab tools to an MCP-capable client."""
from mcp.server.fastmcp import FastMCP
from reference_ranges import classify_value, lookup_range, units_match
from services.gemini_service import AIConfigurationError, generate_explanation

mcp = FastMCP("Clinical Lab Results Analyzer")


def reference_range_lookup_impl(test_name: str) -> dict:
    lab_range = lookup_range(test_name)
    if not lab_range:
        return {"found": False, "message": f"Unknown test: {test_name}"}
    return {
        "found": True,
        "test_name": lab_range.canonical_name,
        "expected_unit": lab_range.unit,
        "reference_range": lab_range.display_range,
        "normal": [lab_range.normal_low, lab_range.normal_high],
        "warning": [lab_range.warning_low, lab_range.warning_high],
        "critical": [lab_range.critical_low, lab_range.critical_high],
    }


def classify_lab_result_impl(test_name: str, value: float, unit: str) -> dict:
    lab_range = lookup_range(test_name)
    if not lab_range:
        return {"found": False, "message": f"Unknown lab test: {test_name}"}
    if not units_match(unit, lab_range.unit):
        return {"found": False, "message": f"Unit for {lab_range.canonical_name} must be {lab_range.unit}"}
    return {
        "found": True,
        "test_name": lab_range.canonical_name,
        "value": value,
        "unit": lab_range.unit,
        "status": classify_value(lab_range, value),
        "reference_range": lab_range.display_range,
        "normal_low": lab_range.normal_low,
        "normal_high": lab_range.normal_high,
    }


@mcp.tool()
def reference_range_lookup(test_name: str) -> dict:
    """Look up the supported lab's deterministic adult demo reference intervals."""
    return reference_range_lookup_impl(test_name)


@mcp.tool()
def classify_lab_result(test_name: str, value: float, unit: str) -> dict:
    """Classify a lab using fixed reference ranges. This is never delegated to an LLM."""
    return classify_lab_result_impl(test_name, value, unit)


@mcp.tool()
async def explain_lab_result(test_name: str, value: float, unit: str, status: str, reference_range: str) -> dict:
    """Use Gemini to explain a pre-classified result without changing its status."""
    result = {"test_name": test_name, "value": value, "unit": unit, "status": status, "reference_range": reference_range}
    try:
        explanation, next_step = await generate_explanation(result)
        return {"ok": True, "explanation": explanation, "next_step": next_step}
    except AIConfigurationError as error:
        return {"ok": False, "error": str(error)}


if __name__ == "__main__":
    mcp.run()
