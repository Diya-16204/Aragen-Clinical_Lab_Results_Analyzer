import json
import os
import requests


class AIConfigurationError(RuntimeError):
    """Raised when a required live LLM explanation cannot be produced."""


async def generate_explanation(result: dict) -> tuple[str, str]:
    prompt = f'''You are a clinical decision-support writing assistant. Explain the fixed classification below.
Do not diagnose. Do not change or invent reference ranges. Do not say this proves a disease.
Return ONLY valid JSON with string fields "explanation" and "next_step". Keep each under 55 words.
Input: {json.dumps(result)}'''
    provider = os.getenv("AI_PROVIDER", "gemini").strip().lower()
    if provider == "groq":
        return _generate_with_groq(prompt)
    if provider != "gemini":
        raise AIConfigurationError("AI_PROVIDER must be either 'gemini' or 'groq'.")
    return _generate_with_gemini(prompt)


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
