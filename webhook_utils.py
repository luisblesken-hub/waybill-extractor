"""
DocExtract Pro — Webhook delivery
Sends extraction results to customer-configured endpoints
"""
import hmac
import hashlib
import json
import time
import httpx
from typing import Optional
from schemas import WaybillData


def _sign_payload(payload: str, secret: str) -> str:
    """HMAC-SHA256 signature for webhook verification."""
    return hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()


def deliver_webhook(
    url: str,
    secret: str,
    event: str,
    data: dict,
    max_retries: int = 3
) -> bool:
    """
    Deliver webhook with retry logic and signature.
    Returns True if successful.
    """
    payload = json.dumps({
        "event":     event,
        "timestamp": int(time.time()),
        "data":      data
    }, ensure_ascii=False)

    signature = _sign_payload(payload, secret)

    headers = {
        "Content-Type":            "application/json",
        "X-DocExtract-Signature":  f"sha256={signature}",
        "X-DocExtract-Event":      event,
        "User-Agent":              "DocExtract-Pro/1.0",
    }

    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(url, content=payload, headers=headers)
                if resp.status_code < 300:
                    return True
        except Exception:
            pass
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff

    return False


def build_extraction_event(
    data: WaybillData,
    filename: str,
    success: bool,
    latency_s: float,
    fields_count: int
) -> dict:
    """Build standardized webhook payload for extraction events."""
    return {
        "filename":        filename,
        "success":         success,
        "latency_s":       latency_s,
        "fields_extracted": fields_count,
        "document_type":   data.document_type,
        "document_number": data.document_number,
        "shipper":         data.shipper.name if data.shipper else None,
        "consignee":       data.consignee.name if data.consignee else None,
        "vessel_name":     data.vessel_name,
        "port_of_loading": data.port_of_loading,
        "port_of_discharge": data.port_of_discharge,
        "eta":             data.eta,
        "container_count": len(data.containers),
        "container_numbers": [c.container_number for c in data.containers if c.container_number],
        "gross_weight_kg": data.gross_weight_kg,
        "full_payload":    data.model_dump(),
    }
