"""
DocExtract Pro — Extraction engine
Zero-hallucination via instructor + Pydantic validation
Auto-retry on failure (max 3 attempts)
"""
import os
import time
from typing import Tuple
import instructor
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
from schemas import WaybillData

load_dotenv()

SYSTEM_PROMPT = """You are a logistics document extraction specialist.
Extract ALL available structured data from the document.
Be precise — only extract what is explicitly stated, never infer or hallucinate.
For missing fields, return null. For dates use ISO-8601 format where possible.
For container numbers follow ISO 6346 format (e.g. MSCU1234567)."""

def _get_instructor_client():
    openai_key    = os.getenv("OPENAI_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

    if openai_key and openai_key.startswith("sk-") and not openai_key.startswith("sk-ant"):
        return "openai", instructor.from_openai(OpenAI(api_key=openai_key)), "gpt-4o-mini"
    elif anthropic_key and anthropic_key.startswith("sk-ant"):
        return "anthropic", instructor.from_anthropic(Anthropic(api_key=anthropic_key)), "claude-haiku-4-5-20251001"
    else:
        raise ValueError("No valid API key found in environment.")

def extract_from_text(text: str, max_retries: int = 3) -> WaybillData:
    """Extract structured logistics data with automatic retry on validation failure."""
    provider, client, model = _get_instructor_client()

    prompt = f"Extract all logistics data from this document:\n\n---\n{text[:8000]}\n---"

    if provider == "openai":
        result = client.chat.completions.create(
            model          = model,
            response_model = WaybillData,
            max_retries    = max_retries,
            messages       = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ]
        )
    else:
        result = client.messages.create(
            model          = model,
            max_tokens     = 4096,
            response_model = WaybillData,
            max_retries    = max_retries,
            messages       = [{"role": "user", "content": f"{SYSTEM_PROMPT}\n\n{prompt}"}]
        )

    return result

def count_extracted_fields(data: WaybillData) -> int:
    """Count non-null fields for quality scoring."""
    count = 0
    for field, value in data.model_dump().items():
        if field == "containers":
            count += len(value)
        elif field == "hs_codes":
            count += len(value)
        elif value is not None and value != "" and value != []:
            count += 1
    return count
