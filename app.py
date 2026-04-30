import streamlit as st
import pdfplumber
import json
import csv
import io
import time
import os
from datetime import datetime
from extractor import extract_from_text

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DocExtract Pro",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Supabase (optional, graceful fallback) ────────────────────────────────────
SUPABASE_ENABLED = bool(os.environ.get("SUPABASE_URL"))
if SUPABASE_ENABLED:
    try:
        from database import sign_in, sign_up, get_credits, deduct_credit, log_usage, get_usage_log, create_api_key, get_api_keys
    except Exception:
        SUPABASE_ENABLED = False

# ── Stripe payment links ──────────────────────────────────────────────────────
STRIPE_LINKS = {
    10:  os.environ.get("STRIPE_10",  "https://buy.stripe.com/placeholder_10"),
    50:  os.environ.get("STRIPE_50",  "https://buy.stripe.com/placeholder_50"),
    200: os.environ.get("STRIPE_200", "https://buy.stripe.com/placeholder_200"),
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.hero {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    padding: 2.5rem 2rem; border-radius: 16px; color: white; margin-bottom: 2rem;
}
.hero h1 { margin: 0; font-size: 2.2rem; font-weight: 700; }
.hero p  { margin: 0.5rem 0 0; opacity: 0.8; font-size: 1.1rem; }

.stat-box {
    background: white; border: 1px solid #e5e7eb;
    border-radius: 12px; padding: 1.2rem; text-align: center;
}
.stat-num   { font-size: 2rem; font-weight: 700; color: #1d4ed8; }
.stat-label { font-size: 0.8rem; color: #6b7280; text-transform: uppercase; }

.credit-box {
    background: linear-gradient(135deg, #1d4ed8, #2563eb);
    border-radius: 12px; padding: 1.5rem; color: white; text-align: center;
}
.credit-num { font-size: 3rem; font-weight: 700; }

.plan-card {
    border: 2px solid #e5e7eb; border-radius: 12px; padding: 1.5rem;
    text-align: center; cursor: pointer; transition: all 0.2s;
}
.plan-card:hover { border-color: #3b82f6; box-shadow: 0 4px 12px rgba(59,130,246,0.2); }
.plan-price { font-size: 2rem; font-weight: 700; color: #1d4ed8; }

.field-group { margin-bottom: 0.9rem; }
.field-label { font-size: 0.72rem; font-weight: 600; color: #9ca3af; text-transform: uppercase; }
.field-value { font-size: 0.97rem; font-weight: 500; color: #111827; margin-top: 2px; }
.field-empty { font-size: 0.97rem; color: #d1d5db; }

div[data-testid="stFileUploader"] {
    border: 2px dashed #3b82f6; border-radius: 12px; padding: 1rem; background: #eff6ff;
}
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
for k, v in [("user", None), ("access_token", None), ("user_id", None),
              ("history", []), ("total_docs", 0), ("total_time", 0.0),
              ("page", "app")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Auth helpers ──────────────────────────────────────────────────────────────
def is_logged_in():
    return st.session_state.user is not None or not SUPABASE_ENABLED

def get_user_credits():
    if not SUPABASE_ENABLED or not st.session_state.user_id:
        return 999  # Unlimited in demo mode
    return get_credits(st.session_state.user_id)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚢 DocExtract Pro")
    st.markdown("*Enterprise Logistik-KI*")
    st.divider()

    if SUPABASE_ENABLED and is_logged_in() and st.session_state.user:
        credits = get_user_credits()
        st.markdown(f"""
        <div class="credit-box">
            <div style="font-size:0.8rem;opacity:0.8;">VERFÜGBARE CREDITS</div>
            <div class="credit-num">{credits}</div>
            <div style="font-size:0.85rem;opacity:0.8;">= €{credits * 0.49:.2f} Wert</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("💳 Credits kaufen", use_container_width=True):
            st.session_state.page = "billing"
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
        if st.button("🔑 API Keys", use_container_width=True):
            st.session_state.page = "api_keys"
        if st.button("📄 Extrahieren", use_container_width=True):
            st.session_state.page = "app"
        st.divider()
        if st.button("Abmelden", use_container_width=True):
            st.session_state.user = None
            st.session_state.user_id = None
            st.rerun()
    else:
        st.markdown("**Dokument-Typen**")
        for doc in ["Sea Waybills", "Bills of Lading", "Commercial Invoices", "Packing Lists"]:
            st.markdown(f"✓ {doc}")
        st.divider()
        st.markdown("**15+ Felder**")
        for f in ["Absender / Empfänger", "Schiff & Voyage", "Container", "Häfen & Daten", "Gewicht & HS-Codes"]:
            st.markdown(f"• {f}")
        st.divider()

    if st.session_state.total_docs > 0:
        avg = st.session_state.total_time / st.session_state.total_docs
        st.metric("Verarbeitet", st.session_state.total_docs)
        st.metric("Ø Zeit", f"{avg:.1f}s")
    st.caption("Powered by Claude AI · v3.0")

# ── Login Page ────────────────────────────────────────────────────────────────
def show_login():
    st.markdown("""
    <div class="hero">
        <h1>🚢 DocExtract Pro</h1>
        <p>Enterprise Logistik-Dokumentenextraktion — KI-powered, sofort einsatzbereit.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Anmelden", "Registrieren"])

        with tab1:
            email    = st.text_input("E-Mail", key="login_email")
            password = st.text_input("Passwort", type="password", key="login_pw")
            if st.button("Anmelden", type="primary", use_container_width=True):
                try:
                    res = sign_in(email, password)
                    st.session_state.user    = res.user
                    st.session_state.user_id = str(res.user.id)
                    st.rerun()
                except Exception as e:
                    st.error(f"Fehler: {e}")

        with tab2:
            email2 = st.text_input("E-Mail", key="reg_email")
            pw2    = st.text_input("Passwort", type="password", key="reg_pw")
            if st.button("Konto erstellen", type="primary", use_container_width=True):
                try:
                    res = sign_up(email2, pw2)
                    st.success("✅ Bestätigungs-E-Mail gesendet. Bitte verifizieren.")
                except Exception as e:
                    st.error(f"Fehler: {e}")

        st.markdown("---")
        st.markdown("**Demo ohne Konto:** Direkt loslegen — 3 kostenlose Extraktionen.")
        if st.button("Demo starten", use_container_width=True):
            st.session_state.user    = "demo"
            st.session_state.user_id = None
            st.rerun()

# ── Billing Page ──────────────────────────────────────────────────────────────
def show_billing():
    st.markdown("## 💳 Credits kaufen")
    st.markdown("**€0.49 pro erfolgreich extrahiertem Dokument**")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    plans = [
        (col1, 10,  "4.90", "Starter",    "Für den Einstieg"),
        (col2, 50,  "19.90", "Business",  "Beliebteste Wahl", True),
        (col3, 200, "69.90", "Enterprise", "Für hohes Volumen"),
    ]
    for col, credits, price, name, desc, *popular in plans:
        with col:
            badge = "⭐ " if popular else ""
            st.markdown(f"""
            <div class="plan-card">
                <div style="font-size:1.1rem;font-weight:700;">{badge}{name}</div>
                <div class="plan-price">€{price}</div>
                <div style="color:#6b7280;">{credits} Credits</div>
                <div style="font-size:0.85rem;margin-top:0.5rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            link = STRIPE_LINKS.get(credits, "#")
            st.markdown(f"<br><a href='{link}' target='_blank'><button style='width:100%;background:#1d4ed8;color:white;border:none;padding:0.6rem;border-radius:8px;font-weight:600;cursor:pointer;'>Jetzt kaufen</button></a>", unsafe_allow_html=True)

    st.markdown("---")
    st.info("Nach dem Kauf erscheinen Credits automatisch auf deinem Konto (via Stripe Webhook).")

# ── Dashboard Page ────────────────────────────────────────────────────────────
def show_dashboard():
    st.markdown("## 📊 Dashboard")
    if not SUPABASE_ENABLED or not st.session_state.user_id:
        st.info("Dashboard verfügbar nach Anmeldung.")
        return

    logs = get_usage_log(st.session_state.user_id)
    total_docs    = len(logs)
    total_spent   = sum(l["cost_eur"] for l in logs)
    success_rate  = (sum(1 for l in logs if l["success"]) / total_docs * 100) if total_docs else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{total_docs}</div><div class="stat-label">Dokumente</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-num">€{total_spent:.2f}</div><div class="stat-label">Ausgegeben</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{success_rate:.0f}%</div><div class="stat-label">Erfolgsrate</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Letzte Extraktionen")
    for log in logs[:20]:
        st.markdown(
            f"`{log['created_at'][:16]}` &nbsp; **{log['filename'] or '—'}** &nbsp; "
            f"`{log['doc_type']}` &nbsp; {'✅' if log['success'] else '❌'} &nbsp; "
            f"{log['latency_s']}s &nbsp; €{log['cost_eur']:.2f}"
        )

# ── API Keys Page ─────────────────────────────────────────────────────────────
def show_api_keys():
    st.markdown("## 🔑 API Keys")
    st.markdown("Nutze die DocExtract API direkt in deinen Systemen.")

    if not SUPABASE_ENABLED or not st.session_state.user_id:
        st.info("API Keys verfügbar nach Anmeldung.")
        return

    st.markdown("### API Docs")
    st.code("""
# Extraktion per API
curl -X POST https://waybil-wqgbsxbcmfkfdzqswciqqp.streamlit.app/api/extract \\
  -H "Authorization: Bearer dxp_YOUR_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"text": "SEA WAYBILL NO: SWB-001..."}'
""", language="bash")

    st.markdown("---")
    name = st.text_input("Key-Name (z.B. 'SAP Integration')")
    if st.button("🔑 Neuen API Key erstellen", type="primary"):
        if name:
            key = create_api_key(st.session_state.user_id, name)
            st.success(f"✅ Key erstellt — nur einmal sichtbar:")
            st.code(key)
            st.warning("Diesen Key sofort speichern — er wird nicht mehr angezeigt!")

    st.markdown("### Bestehende Keys")
    for k in get_api_keys(st.session_state.user_id):
        st.markdown(f"**{k['name']}** · `{k['key_prefix']}...` · erstellt {k['created_at'][:10]}")

# ── Main App ──────────────────────────────────────────────────────────────────
def show_app():
    st.markdown("""
    <div class="hero">
        <h1>🚢 DocExtract Pro</h1>
        <p>Logistikdokumente in Sekunden auslesen — kein manuelles Abtippen, 0 Fehler.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="stat-box"><div class="stat-num">{st.session_state.total_docs}</div><div class="stat-label">Verarbeitet</div></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="stat-box"><div class="stat-num">15+</div><div class="stat-label">Felder</div></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="stat-box"><div class="stat-num">CSV</div><div class="stat-label">& JSON Export</div></div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="stat-box"><div class="stat-num">∞</div><div class="stat-label">Batch-Upload</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Credit check
    if SUPABASE_ENABLED and st.session_state.user_id:
        credits = get_user_credits()
        if credits <= 0:
            st.warning("⚠️ Keine Credits mehr. Bitte kaufe neue Credits.")
            if st.button("💳 Credits kaufen"):
                st.session_state.page = "billing"
                st.rerun()
            return

    uploaded_files = st.file_uploader(
        "📂 PDFs hochladen (Mehrfachauswahl möglich)",
        type=["pdf"], accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            if any(h["filename"] == uploaded_file.name for h in st.session_state.history):
                continue

            st.markdown(f"---\n### 📄 {uploaded_file.name}")

            with st.spinner("Text wird gelesen..."):
                with pdfplumber.open(uploaded_file) as pdf:
                    text = "\n".join(p.extract_text() or "" for p in pdf.pages)

            if not text.strip():
                st.warning("⚠️ Kein Text — Scan-PDF ohne OCR.")
                continue

            with st.expander("Roher PDF-Text"):
                st.text(text[:4000])

            with st.spinner("🤖 Claude analysiert..."):
                t0 = time.time()
                try:
                    # Deduct credit
                    if SUPABASE_ENABLED and st.session_state.user_id:
                        if not deduct_credit(st.session_state.user_id):
                            st.error("Keine Credits mehr.")
                            break

                    data    = extract_from_text(text)
                    elapsed = round(time.time() - t0, 1)

                    st.session_state.total_docs += 1
                    st.session_state.total_time += elapsed
                    st.session_state.history.append({
                        "filename": uploaded_file.name,
                        "doc_type": data.document_type,
                        "doc_number": data.document_number,
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "elapsed": elapsed,
                    })

                    if SUPABASE_ENABLED and st.session_state.user_id:
                        log_usage(st.session_state.user_id, uploaded_file.name,
                                  data.document_type, data.document_number or "", True, elapsed)

                    st.markdown(f'<span style="background:#dcfce7;color:#166534;padding:3px 10px;border-radius:20px;font-size:0.8rem;font-weight:600;">✅ {elapsed}s</span>', unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown("#### 📋 Dokument")
                        for label, value in [("Typ", data.document_type), ("Nummer", data.document_number),
                                              ("Absender", data.shipper), ("Empfänger", data.consignee), ("Notify", data.notify_party)]:
                            v = f'<div class="field-value">{value}</div>' if value else '<div class="field-empty">—</div>'
                            st.markdown(f'<div class="field-group"><div class="field-label">{label}</div>{v}</div>', unsafe_allow_html=True)

                    with col2:
                        st.markdown("#### 🚢 Transport")
                        for label, value in [("Schiff", data.vessel_name), ("Voyage", data.voyage_number),
                                              ("POL", data.port_of_loading), ("POD", data.port_of_discharge),
                                              ("ETD", data.etd), ("ETA", data.eta)]:
                            v = f'<div class="field-value">{value}</div>' if value else '<div class="field-empty">—</div>'
                            st.markdown(f'<div class="field-group"><div class="field-label">{label}</div>{v}</div>', unsafe_allow_html=True)

                    with col3:
                        st.markdown("#### 📦 Ladung")
                        for label, value in [("Ware", data.cargo_description),
                                              ("Gewicht kg", str(data.gross_weight_kg) if data.gross_weight_kg else None),
                                              ("CBM", str(data.measurement_cbm) if data.measurement_cbm else None),
                                              ("Fracht", data.freight_terms),
                                              ("HS-Codes", ", ".join(data.hs_codes) if data.hs_codes else None)]:
                            v = f'<div class="field-value">{value}</div>' if value else '<div class="field-empty">—</div>'
                            st.markdown(f'<div class="field-group"><div class="field-label">{label}</div>{v}</div>', unsafe_allow_html=True)

                    if data.containers:
                        st.markdown("**Container:**")
                        for c in data.containers:
                            st.markdown(f"`{c.container_number or '?'}` · {c.container_type or '—'} · Seal: {c.seal_number or '—'}")

                    st.markdown("---")
                    flat = data.model_dump()
                    flat["containers"] = json.dumps(flat["containers"], ensure_ascii=False)
                    flat["hs_codes"]   = ", ".join(flat["hs_codes"])

                    buf = io.StringIO()
                    csv.DictWriter(buf, fieldnames=flat.keys()).writeheader() or csv.DictWriter(buf, fieldnames=flat.keys()).writerow(flat)
                    buf.seek(0); writer = csv.DictWriter(buf, fieldnames=flat.keys()); writer.writeheader(); writer.writerow(flat)

                    ec1, ec2 = st.columns(2)
                    with ec1:
                        st.download_button("📥 CSV", buf.getvalue(), f"{data.document_number or 'doc'}.csv", "text/csv", use_container_width=True)
                    with ec2:
                        st.download_button("📥 JSON", json.dumps(data.model_dump(), ensure_ascii=False, indent=2),
                                           f"{data.document_number or 'doc'}.json", "application/json", use_container_width=True)

                except Exception as e:
                    st.error(f"❌ Fehler: {e}")

    if st.session_state.history:
        st.markdown("---\n## 📋 Session-History")
        for h in reversed(st.session_state.history):
            st.markdown(f"`{h['timestamp']}` · **{h['filename']}** · `{h['doc_type']}` · ⏱ {h['elapsed']}s")

# ── Router ────────────────────────────────────────────────────────────────────
if not is_logged_in() and SUPABASE_ENABLED:
    show_login()
elif st.session_state.page == "billing":
    show_billing()
elif st.session_state.page == "dashboard":
    show_dashboard()
elif st.session_state.page == "api_keys":
    show_api_keys()
else:
    show_app()
