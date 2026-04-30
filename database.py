"""
DocExtract Pro — Supabase database layer
Handles: auth, credits, usage logging, API keys, webhooks
"""
import os
import hashlib
import secrets
from datetime import datetime
from typing import Optional
from supabase import create_client, Client

def get_client() -> Client:
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_ANON_KEY", "")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL or SUPABASE_ANON_KEY not set")
    return create_client(url, key)

# ── Auth ──────────────────────────────────────────────────────────────────────

def sign_up(email: str, password: str):
    return get_client().auth.sign_up({"email": email, "password": password})

def sign_in(email: str, password: str):
    return get_client().auth.sign_in_with_password({"email": email, "password": password})

def reset_password(email: str):
    return get_client().auth.reset_password_email(email)

# ── Credits ───────────────────────────────────────────────────────────────────

def get_credits(user_id: str) -> int:
    sb = get_client()
    res = sb.table("credits").select("balance").eq("user_id", user_id).execute()
    if res.data:
        return res.data[0]["balance"]
    sb.table("credits").insert({"user_id": user_id, "balance": 0}).execute()
    return 0

def add_credits(user_id: str, amount: int) -> int:
    sb = get_client()
    current = get_credits(user_id)
    new_balance = current + amount
    sb.table("credits").upsert({
        "user_id": user_id,
        "balance": new_balance,
        "updated_at": datetime.utcnow().isoformat()
    }).execute()
    return new_balance

def deduct_credit(user_id: str) -> bool:
    sb = get_client()
    current = get_credits(user_id)
    if current <= 0:
        return False
    sb.table("credits").update({
        "balance": current - 1,
        "updated_at": datetime.utcnow().isoformat()
    }).eq("user_id", user_id).execute()
    return True

# ── Usage Log ─────────────────────────────────────────────────────────────────

def log_usage(user_id: str, filename: str, doc_type: str, doc_number: str,
              success: bool, latency_s: float, fields_extracted: int = 0):
    get_client().table("usage_log").insert({
        "user_id":          user_id,
        "filename":         filename,
        "doc_type":         doc_type,
        "doc_number":       doc_number,
        "success":          success,
        "latency_s":        round(latency_s, 2),
        "fields_extracted": fields_extracted,
        "cost_eur":         0.49 if success else 0.0,
        "created_at":       datetime.utcnow().isoformat()
    }).execute()

def get_usage_log(user_id: str, limit: int = 100) -> list:
    res = get_client().table("usage_log")\
        .select("*")\
        .eq("user_id", user_id)\
        .order("created_at", desc=True)\
        .limit(limit)\
        .execute()
    return res.data or []

def get_usage_stats(user_id: str) -> dict:
    logs = get_usage_log(user_id, limit=1000)
    total       = len(logs)
    successful  = sum(1 for l in logs if l["success"])
    total_spent = sum(l["cost_eur"] for l in logs)
    avg_latency = sum(l["latency_s"] for l in logs) / total if total else 0
    doc_types   = {}
    for l in logs:
        doc_types[l["doc_type"]] = doc_types.get(l["doc_type"], 0) + 1
    return {
        "total": total,
        "successful": successful,
        "success_rate": (successful / total * 100) if total else 0,
        "total_spent": round(total_spent, 2),
        "avg_latency": round(avg_latency, 2),
        "doc_types": doc_types,
    }

# ── API Keys ──────────────────────────────────────────────────────────────────

def create_api_key(user_id: str, name: str) -> str:
    key      = "dxp_" + secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    get_client().table("api_keys").insert({
        "user_id":    user_id,
        "name":       name,
        "key_hash":   key_hash,
        "key_prefix": key[:16],
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    return key

def get_api_keys(user_id: str) -> list:
    res = get_client().table("api_keys")\
        .select("id, name, key_prefix, created_at, last_used_at")\
        .eq("user_id", user_id)\
        .execute()
    return res.data or []

def revoke_api_key(key_id: str, user_id: str):
    get_client().table("api_keys")\
        .delete()\
        .eq("id", key_id)\
        .eq("user_id", user_id)\
        .execute()

def validate_api_key(key: str) -> Optional[str]:
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    res = get_client().table("api_keys")\
        .select("user_id")\
        .eq("key_hash", key_hash)\
        .execute()
    if res.data:
        get_client().table("api_keys").update({
            "last_used_at": datetime.utcnow().isoformat()
        }).eq("key_hash", key_hash).execute()
        return res.data[0]["user_id"]
    return None

# ── Webhooks ──────────────────────────────────────────────────────────────────

def save_webhook(user_id: str, url: str, events: list) -> str:
    res = get_client().table("webhooks").insert({
        "user_id":    user_id,
        "url":        url,
        "events":     events,
        "secret":     secrets.token_urlsafe(24),
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    return res.data[0]["id"] if res.data else ""

def get_webhooks(user_id: str) -> list:
    res = get_client().table("webhooks")\
        .select("id, url, events, created_at")\
        .eq("user_id", user_id)\
        .execute()
    return res.data or []
