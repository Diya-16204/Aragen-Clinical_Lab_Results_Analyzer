import json
import os
import requests


class AIConfigurationError(RuntimeError):
    """Raised when a required live LLM explanation cannot be produced."""


def language_instruction(language: str) -> str:
    return "Write all natural-language fields in simple, patient-friendly Hindi using Devanagari script." if language == "hi" else "Write all natural-language fields in English."


async def generate_explanation(result: dict, language: str = "en") -> tuple[str, str]:
    prompt = f'''You are a clinical decision-support writing assistant. Explain the fixed classification below.
Do not diagnose. Do not change or invent reference ranges. Do not say this proves a disease.
Return ONLY valid JSON with string fields "explanation" and "next_step". Keep each under 55 words.
{language_instruction(language)} Preserve every supplied number, unit, reference range, and deterministic status exactly.
Input: {json.dumps(result)}'''
    provider = os.getenv("AI_PROVIDER", "gemini").strip().lower()
    if provider == "groq":
        return _generate_with_groq(prompt)
    if provider != "gemini":
        raise AIConfigurationError("AI_PROVIDER must be either 'gemini' or 'groq'.")
    return _generate_with_gemini(prompt)


async def generate_overall_summary(results: list[dict], language: str = "en") -> str:
    """Create a narrative across fixed, already-classified lab results."""
    prompt = f'''You are a clinical decision-support writing assistant. Write one concise overall analysis summary for the provided, already-classified lab results.
Use only supplied facts. Do not change classifications, invent ranges, history, symptoms, diagnoses, medications, or values. Do not name or imply any disease (for example, do not write anemia, diabetes, renal failure, or infection). Describe only the measured finding and deterministic severity. Prioritize CRITICAL findings, then WARNING findings, and distinguish normal findings. Recommend clinical review/follow-up rather than unsafe instructions. End with: "Informational decision support; not a substitute for professional clinical judgment."
Return ONLY valid JSON: {{"summary":"..."}}.
{language_instruction(language)} Preserve every supplied number, unit, reference range, and deterministic status exactly.
Results: {json.dumps(results)}'''
    provider = os.getenv("AI_PROVIDER", "gemini").strip().lower()
    try:
        if provider == "groq":
            return _generate_summary_with_groq(prompt)
        if provider == "gemini":
            return _generate_summary_with_gemini(prompt)
        raise AIConfigurationError("AI_PROVIDER must be either 'gemini' or 'groq'.")
    except Exception as error:
        if isinstance(error, AIConfigurationError):
            raise
        raise AIConfigurationError(f"Overall summary generation failed: {error}") from error


async def ask_aragen_doc(question: str, lab_results: list[dict], language: str = "en") -> dict:
    """Answer a constrained informational question using current analyzed results only."""
    blocked = ("medicine", "medication", "drug", "dose", "dosage", "prescribe", "change my", "change the status", "दवा", "खुराक", "स्थिति बदल")
    if any(term in question.lower() for term in blocked):
        if language == "hi":
            return {"answer": "मैं केवल लैब परिणामों के आधार पर दवा या उसकी खुराक नहीं बता सकता। कृपया योग्य स्वास्थ्य-विशेषज्ञ से परामर्श करें। इस ऐप के वर्गीकरण नियम-आधारित संदर्भ सीमाओं से तय होते हैं और इन्हें बदला नहीं जा सकता।", "suggested_specialist": None, "safety_note": "यह केवल जानकारी है; यह निदान, पर्चा या उपचार योजना नहीं है।"}
        return {"answer": "I cannot prescribe medication or dosages based on laboratory results alone. Please consult a qualified healthcare professional. The application's classifications are determined by rule-based reference ranges and cannot be changed by this assistant.", "suggested_specialist": None, "safety_note": "Informational guidance only; not a diagnosis, prescription, or treatment plan."}
    prompt = f'''You are Aragen Doc, an AI-powered laboratory-results information assistant. Use ONLY the provided laboratory context.
Explain what supplied abnormal values can generally indicate without diagnosing. You may suggest a relevant type of specialist and questions to ask a doctor. Do not prescribe medications, doses, treatment changes, diagnoses, or invent facts. Do not alter Normal/Warning/Critical classification. Clearly distinguish supplied abnormal and normal findings.
Return ONLY valid JSON with strings: "answer", "suggested_specialist", "safety_note". safety_note must state that this is informational and not a diagnosis or prescription.
Question: {question}
{language_instruction(language)} Preserve every supplied number, unit, reference range, and deterministic status exactly.
Current analyzed results: {json.dumps(lab_results)}'''
    provider = os.getenv("AI_PROVIDER", "gemini").strip().lower()
    try:
        if provider == "groq":
            return _generate_doc_with_groq(prompt)
        if provider == "gemini":
            return _generate_doc_with_gemini(prompt)
        raise AIConfigurationError("AI_PROVIDER must be either 'gemini' or 'groq'.")
    except Exception as error:
        if isinstance(error, AIConfigurationError):
            raise
        raise AIConfigurationError(f"Aragen Doc request failed: {error}") from error


def _validate_payload(payload: dict) -> tuple[str, str]:
    if isinstance(payload.get("explanation"), str) and isinstance(payload.get("next_step"), str):
        return payload["explanation"], payload["next_step"]
    raise ValueError("LLM returned an incomplete explanation.")


def _generate_with_gemini(prompt: str) -> tuple[str, str]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise AIConfigurationError("GEMINI_API_KEY is required when AI_PROVIDER=gemini.")
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"), contents=prompt,
            config={"response_mime_type": "application/json"},
        )
        return _validate_payload(json.loads(response.text))
    except Exception as error:
        raise AIConfigurationError(f"Gemini explanation request failed: {error}") from error


def _generate_summary_with_gemini(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise AIConfigurationError("GEMINI_API_KEY is required when AI_PROVIDER=gemini.")
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"), contents=prompt,
                                                  config={"response_mime_type": "application/json"})
        return _validate_summary(json.loads(response.text))
    except Exception as error:
        raise AIConfigurationError(f"Gemini overall summary request failed: {error}") from error


def _validate_doc(payload: dict) -> dict:
    if not isinstance(payload.get("answer"), str) or not payload["answer"].strip():
        raise ValueError("LLM returned an invalid Aragen Doc response.")
    return {"answer": payload["answer"].strip(), "suggested_specialist": payload.get("suggested_specialist") if isinstance(payload.get("suggested_specialist"), str) else None,
            "safety_note": payload.get("safety_note") if isinstance(payload.get("safety_note"), str) else "Informational guidance only; not a diagnosis, prescription, or treatment plan."}


def _generate_doc_with_gemini(prompt: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise AIConfigurationError("GEMINI_API_KEY is required when AI_PROVIDER=gemini.")
    try:
        from google import genai
        response = genai.Client(api_key=api_key).models.generate_content(model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"), contents=prompt,
            config={"response_mime_type": "application/json"})
        return _validate_doc(json.loads(response.text))
    except Exception as error:
        raise AIConfigurationError(f"Gemini Aragen Doc request failed: {error}") from error


def _generate_with_groq(prompt: str) -> tuple[str, str]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise AIConfigurationError("GROQ_API_KEY is required when AI_PROVIDER=groq.")
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
                "messages": [{"role": "system", "content": "Return only valid JSON."}, {"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"},
                "temperature": 0.2,
            },
            timeout=30,
        )
        if not response.ok:
            # Groq uses detailed JSON error bodies for model, account, and
            # endpoint failures. Return that safe provider diagnostic to the UI.
            raise RuntimeError(f"HTTP {response.status_code}: {response.text[:500]}")
        content = response.json()["choices"][0]["message"]["content"]
        return _validate_payload(json.loads(content))
    except Exception as error:
        raise AIConfigurationError(f"Groq explanation request failed: {error}") from error


def _validate_summary(payload: dict) -> str:
    summary = payload.get("summary")
    if isinstance(summary, str) and summary.strip():
        return summary.strip()
    raise ValueError("LLM returned an empty overall summary.")


def _generate_summary_with_groq(prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise AIConfigurationError("GROQ_API_KEY is required when AI_PROVIDER=groq.")
    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
                  "messages": [{"role": "system", "content": "Return only valid JSON."}, {"role": "user", "content": prompt}],
                  "response_format": {"type": "json_object"}, "temperature": 0.2}, timeout=30)
        if not response.ok:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text[:500]}")
        return _validate_summary(json.loads(response.json()["choices"][0]["message"]["content"]))
    except Exception as error:
        raise AIConfigurationError(f"Groq overall summary request failed: {error}") from error


def _generate_doc_with_groq(prompt: str) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise AIConfigurationError("GROQ_API_KEY is required when AI_PROVIDER=groq.")
    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"), "messages": [{"role": "system", "content": "Return only valid JSON."}, {"role": "user", "content": prompt}],
                  "response_format": {"type": "json_object"}, "temperature": 0.2}, timeout=30)
        if not response.ok:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text[:500]}")
        return _validate_doc(json.loads(response.json()["choices"][0]["message"]["content"]))
    except Exception as error:
        raise AIConfigurationError(f"Groq Aragen Doc request failed: {error}") from error
