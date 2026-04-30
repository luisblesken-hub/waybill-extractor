"""
Supabase database layer for DocExtract Pro.
Handles users, credits, usage tracking, API keys.
"""
import os
import hashlib
import secrets
from datetime import datetime
from typing import Optional
from supabase import create_client, Client

def get_client() -> Client:
    url  = os.environ["SUPABASE_URL"]
    key  = os.environ["SUPABASE_ANON_KEY"]
    return create_client(url, key)

# ── Auth ──────────────────────────────────────────────────────────────────────

def sign_up(email: str, password: str) -> dict:
    sb = get_client()
    res = sb.auth.sign_up({"email": email, "password": password})
    return res

def sign_in(email: str, password: str) -> dict:
    sb = get_client()
    res = sb.auth.sign_in_with_password({"email": email, "password": password})
    return res

def sign_out(access_token: str):
    sb = get_client()
    sb.auth.sign_out()

# ── Credits ───────────────────────────────────────────────────────────────────

def get_credits(user_id: str) -> int:
    sb = get_client()
    res = sb.table("credits").select("balance").eq("user_id", user_id).single().execute()
    if res.data:
        return res.data["balance"]
    # Create record if not exists
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
    """Returns True if credit deducted, False if insufficient."""
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
              success: bool, latency_s: float):
    sb = get_client()
    sb.table("usage_log").insert({
        "user_id":    user_id,
        "filename":   filename,
        "doc_type":   doc_type,
        "doc_number": doc_number,
        "success":    success,
        "latency_s":  round(latency_s, 2),
        "cost_eur":   0.49 if success else 0.0,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

def get_usage_log(user_id: str, limit: int = 50) -> list:
    sb = get_client()
    res = sb.table("usage_log")\
        .select("*")\
        .eq("user_id", user_id)\
        .order("created_at", desc=True)\
        .limit(limit)\
        .execute()
    return res.data or []

# ── API Keys ──────────────────────────────────────────────────────────────────

def create_api_key(user_id: str, name: str) -> str:
    sb = get_client()
    key = "dxp_" + secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    sb.table("api_keys").insert({
        "user_id":    user_id,
        "name":       name,
        "key_hash":   key_hash,
        "key_prefix": key[:12],
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    return key  # Only shown once

def get_api_keys(user_id: str) -> list:
    sb = get_client()
    res = sb.table("api_keys")\
        .select("id, name, key_prefix, created_at, last_used_at")\
        .eq("user_id", user_id)\
        .execute()
    return res.data or []

def validate_api_key(key: str) -> Optional[str]:
    """Returns user_id if valid, None if invalid."""
    sb = get_client()
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    res = sb.table("api_keys")\
        .select("user_id")\
        .eq("key_hash", key_hash)\
        .single()\
        .execute()
    if res.data:
        # Update last_used_at
        sb.table("api_keys").update({
            "last_used_at": datetime.utcnow().isoformat()
        }).eq("key_hash", key_hash).execute()
        return res.data["user_id"]
    return None
