import os
import instructor
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv
from schemas import WaybillData

load_dotenv()

def extract_from_text(text: str) -> WaybillData:
    """Extrahiert strukturierte Daten aus Dokumenttext."""

    openai_key = os.getenv("OPENAI_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

    if openai_key and openai_key.startswith("sk-") and not openai_key.startswith("sk-ant"):
        client = instructor.from_openai(OpenAI(api_key=openai_key))
        result = client.chat.completions.create(
            model="gpt-4o-mini",
            response_model=WaybillData,
            messages=[{
                "role": "user",
                "content": f"Extrahiere alle Logistikdaten aus diesem Dokument:\n\n{text}"
            }]
        )
    elif anthropic_key and anthropic_key.startswith("sk-ant"):
        client = instructor.from_anthropic(Anthropic(api_key=anthropic_key))
        result = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            response_model=WaybillData,
            messages=[{
                "role": "user",
                "content": f"Extrahiere alle Logistikdaten aus diesem Dokument:\n\n{text}"
            }]
        )
    else:
        raise ValueError("Kein gültiger API Key in .env gefunden.")

    return result
