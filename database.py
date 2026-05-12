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

def get_service_client() -> Client:
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_ANON_KEY", "")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL or SUPABASE_SERVICE_KEY not set")
    return create_client(url, key)

def sign_up(email, password):
    return get_client().auth.sign_up({"email": email, "password": password})

def sign_in(email, password):
    return get_client().auth.sign_in_with_password({"email": email, "password": password})

def reset_password(email):
    return get_client().auth.reset_password_email(email)

def get_credits(user_id: str) -> int:
    ssb = get_service_client()
    res = ssb.table("credits").select("balance").eq("user_id", user_id).execute()
    if res.data:
        return res.data[0]["balance"]
    # New user — initialise with 0 credits (trigger should handle this, fallback here)
    try:
        ssb.table("credits").insert({"user_id": user_id, "balance": 0}).execute()
    except Exception:
        pass
    return 0

def add_credits(user_id, amount):
    ssb = get_service_client()
    current = get_credits(user_id)
    new_balance = current + amount
    ssb.table("credits").upsert({"user_id": user_id, "balance": new_balance, "updated_at": datetime.utcnow().isoformat()}).execute()
    return new_balance

def deduct_credit(user_id):
    ssb = get_service_client()
    current = get_credits(user_id)
    if current <= 0:
        return False
    ssb.table("credits").update({"balance": current - 1, "updated_at": datetime.utcnow().isoformat()}).eq("user_id", user_id).execute()
    return True

def log_usage(user_id, filename, doc_type, doc_number, success, latency_s, fields_extracted=0):
    get_service_client().table("usage_log").insert({"user_id": user_id, "filename": filename, "doc_type": doc_type, "doc_number": doc_number, "success": success, "latency_s": round(latency_s, 2), "fields_extracted": fields_extracted, "cost_eur": 0.49 if success else 0.0, "created_at": datetime.utcnow().isoformat()}).execute()

def get_usage_log(user_id, limit=100):
    res = get_client().table("usage_log").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
    return res.data or []

def get_usage_stats(user_id):
    logs = get_usage_log(user_id, limit=1000)
    total = len(logs)
    successful = sum(1 for l in logs if l["success"])
    total_spent = sum(l["cost_eur"] for l in logs)
    avg_latency = sum(l["latency_s"] for l in logs) / total if total else 0
    doc_types = {}
    for l in logs:
        doc_types[l["doc_type"]] = doc_types.get(l["doc_type"], 0) + 1
    return {"total": total, "successful": successful, "success_rate": (successful / total * 100) if total else 0, "total_spent": round(total_spent, 2), "avg_latency": round(avg_latency, 2), "doc_types": doc_types}

def create_api_key(user_id, name):
    key = "dxp_" + secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    get_service_client().table("api_keys").insert({"user_id": user_id, "name": name, "key_hash": key_hash, "key_prefix": key[:16], "created_at": datetime.utcnow().isoformat()}).execute()
    return key

def get_api_keys(user_id):
    res = get_client().table("api_keys").select("id, name, key_prefix, created_at, last_used_at").eq("user_id", user_id).execute()
    return res.data or []

def revoke_api_key(key_id, user_id):
    get_service_client().table("api_keys").delete().eq("id", key_id).eq("user_id", user_id).execute()

def validate_api_key(key):
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    res = get_client().table("api_keys").select("user_id").eq("key_hash", key_hash).execute()
    if res.data:
        get_service_client().table("api_keys").update({"last_used_at": datetime.utcnow().isoformat()}).eq("key_hash", key_hash).execute()
        return res.data[0]["user_id"]
    return None

def save_webhook(user_id, url, events):
    res = get_service_client().table("webhooks").insert({"user_id": user_id, "url": url, "events": events, "secret": secrets.token_urlsafe(24), "created_at": datetime.utcnow().isoformat()}).execute()
    return res.data[0]["id"] if res.data else ""

def get_webhooks(user_id):
    res = get_client().table("webhooks").select("id, url, events, created_at").eq("user_id", user_id).execute()
    return res.data or []

def log_payment(user_id, stripe_session, credits_bought, amount_eur):
    sb = get_service_client()
    existing = sb.table("payments").select("id").eq("stripe_session", stripe_session).execute()
    if existing.data:
        return False
    sb.table("payments").insert({"user_id": user_id, "stripe_session": stripe_session, "credits_bought": credits_bought, "amount_eur": amount_eur, "status": "completed", "created_at": datetime.utcnow().isoformat()}).execute()
    return True

def get_payments(user_id, limit=50):
    res = get_client().table("payments").select("stripe_session, credits_bought, amount_eur, status, created_at").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
    return res.data or []
