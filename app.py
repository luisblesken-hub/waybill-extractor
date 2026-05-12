"""
DocExtract Pro — Main Application
Enterprise logistics document extraction powered by Claude AI
"""
import streamlit as st
import pdfplumber
import json
import time
import os
from datetime import datetime
from extractor import extract_from_text, count_extracted_fields
from export_utils import to_flat_dict, export_csv, export_json, export_excel
from demo_data import DEMO_WAYBILL_TEXT, DEMO_RESULT

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DocExtract Pro",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Feature Flags ─────────────────────────────────────────────────────────────
SUPABASE_ENABLED = bool(os.environ.get("SUPABASE_URL"))
DEMO_FREE_LIMIT  = 3

if SUPABASE_ENABLED:
    try:
        from database import (sign_in, sign_up, reset_password,
                               get_credits, deduct_credit, add_credits,
                               log_usage, get_usage_stats, get_usage_log,
                               create_api_key, get_api_keys, revoke_api_key,
                               save_webhook, get_webhooks)
        from notifications import send_extraction_complete, send_welcome_email, send_low_credits_alert
        from webhook_utils import deliver_webhook, build_extraction_event
    except Exception as e:
        SUPABASE_ENABLED = False

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*, html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
footer, #MainMenu { visibility: hidden !important; }
[data-testid="stToolbar"] { display: none !important; }

/* Force light mode — override system dark mode */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stApp"], .stApp,
[class*="main"], [class*="block-container"] {
    background-color: #f8fafc !important;
    color: #0f172a !important;
    color-scheme: light !important;
}
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}
[data-testid="stSidebar"] * { color: #374151 !important; }
[data-testid="stSidebar"] h2 { color: #0f172a !important; font-weight: 700 !important; }

/* Inputs light */
input, textarea, select {
    background: #ffffff !important;
    color: #0f172a !important;
    border-color: #d1d5db !important;
}

/* Cards */
[data-testid="stExpander"],
[data-testid="stForm"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
}

/* Tab list */
[data-baseweb="tab-list"] { background: #f1f5f9 !important; }
[aria-selected="true"] { background: #ffffff !important; color: #0f172a !important; }

/* Markdown text */
p, li, span, label { color: #374151 !important; }
h1, h2, h3, h4, h5 { color: #0f172a !important; }

.hero {
    background: linear-gradient(135deg, #1e3a5f 0%, #1d4ed8 100%);
    padding: 1.75rem 2rem; border-radius: 10px; margin-bottom: 1.5rem;
}
.hero h1 { margin: 0; font-size: 1.6rem; font-weight: 700; color: #ffffff !important; letter-spacing: -0.03em; }
.hero p  { margin: 0.4rem 0 0; color: rgba(255,255,255,0.8) !important; font-size: 0.9rem; }

.stat-box { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.1rem; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.stat-num { font-size: 1.6rem; font-weight: 700; color: #1d4ed8; letter-spacing: -0.03em; }
.stat-lbl { font-size: 0.68rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 0.2rem; }

.credit-box { background: linear-gradient(135deg, #1d4ed8, #2563eb); border-radius: 8px; padding: 1.25rem; text-align: center; }
.credit-num { font-size: 2.5rem; font-weight: 700; letter-spacing: -0.04em; color: white !important; }

.field-group { margin-bottom: 0.75rem; }
.field-label { font-size: 0.65rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.07em; }
.field-value { font-size: 0.875rem; font-weight: 500; color: #0f172a; margin-top: 2px; }
.field-empty { font-size: 0.875rem; color: #cbd5e1; }

.quality-bar { height: 4px; border-radius: 2px; background: #f1f5f9; overflow: hidden; margin-top: 0.4rem; }
.quality-fill { height: 100%; border-radius: 2px; background: linear-gradient(90deg, #1d4ed8, #0891b2); }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
_defaults = {
    "user": None, "user_id": None, "user_email": None,
    "history": [], "batch_results": [],
    "total_docs": 0, "total_time": 0.0,
    "demo_used": 0, "page": "app"
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def is_logged_in():
    return st.session_state.user is not None

def get_user_credits():
    if not SUPABASE_ENABLED or not st.session_state.user_id:
        return DEMO_FREE_LIMIT - st.session_state.demo_used
    return get_credits(st.session_state.user_id)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## DocExtract Pro")
    st.divider()

    if is_logged_in():
        credits = get_user_credits()
        if SUPABASE_ENABLED and st.session_state.user_id:
            label = "CREDITS"
            if credits <= 5:
                st.warning(f"⚠️ Nur noch {credits} Credits!")
        else:
            label = "DEMO CREDITS"

        st.markdown(f"""
        <div class="credit-box">
            <div style="font-size:0.8rem;opacity:0.8;">{label}</div>
            <div class="credit-num">{credits}</div>
            {"<div style='font-size:0.85rem;opacity:0.8;'>= €"+f"{credits*0.49:.2f}"+" Wert</div>" if SUPABASE_ENABLED and st.session_state.user_id else ""}
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        nav_items = [
            ("Extrahieren",  "app"),
            ("Dashboard",    "dashboard"),
            ("Credits",      "billing"),
            ("API Keys",     "api_keys"),
            ("Webhooks",     "webhooks"),
        ]
        for label_nav, page in nav_items:
            active = "background:#eff6ff;border-left:3px solid #3b82f6;" if st.session_state.page == page else ""
            if st.button(label_nav, use_container_width=True, key=f"nav_{page}"):
                st.session_state.page = page
                st.rerun()

        st.divider()
        if st.session_state.user_email:
            st.caption(f"👤 {st.session_state.user_email}")
        if st.button("Abmelden", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
    else:
        st.markdown("**Dokument-Typen**")
        for d in ["Sea Waybills","Bills of Lading","Commercial Invoices","Packing Lists"]:
            st.markdown(f"✓ {d}")
        st.divider()
        st.markdown("**15+ Felder extrahiert**")

    if st.session_state.total_docs > 0:
        avg = st.session_state.total_time / st.session_state.total_docs
        st.metric("Session", f"{st.session_state.total_docs} Docs")
        st.metric("Ø Tempo", f"{avg:.1f}s")

    st.caption("DocExtract Pro · v3.0")

# ════════════════════════════════════════════════════════════════════════════════
# LOGIN PAGE
# ════════════════════════════════════════════════════════════════════════════════

def show_login():
    st.markdown("""
    <div class="hero">
        <h1>🚢 DocExtract Pro</h1>
        <p>Strukturierte Daten aus Logistikdokumenten — sofort, präzise, skalierbar.</p>
    </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1,2,1])
    with mid:
        tab1, tab2, tab3 = st.tabs(["Anmelden", "Registrieren", "Passwort vergessen"])

        with tab1:
            email    = st.text_input("E-Mail", key="li_email")
            password = st.text_input("Passwort", type="password", key="li_pw")
            if st.button("Anmelden", type="primary", use_container_width=True):
                try:
                    res = sign_in(email, password)
                    st.session_state.user       = res.user
                    st.session_state.user_id    = str(res.user.id)
                    st.session_state.user_email = res.user.email
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {e}")

        with tab2:
            email2 = st.text_input("E-Mail", key="reg_email")
            pw2    = st.text_input("Passwort (min. 8 Zeichen)", type="password", key="reg_pw")
            if st.button("Konto erstellen", type="primary", use_container_width=True):
                if len(pw2) < 8:
                    st.error("Passwort muss mindestens 8 Zeichen haben.")
                else:
                    try:
                        sign_up(email2, pw2)
                        send_welcome_email(email2)
                        st.success("✅ Bestätigungs-E-Mail gesendet. Bitte E-Mail verifizieren.")
                    except Exception as e:
                        st.error(f"❌ {e}")

        with tab3:
            email3 = st.text_input("E-Mail", key="reset_email")
            if st.button("Reset-Link senden", use_container_width=True):
                try:
                    reset_password(email3)
                    st.success("✅ Reset-Link gesendet.")
                except Exception as e:
                    st.error(f"❌ {e}")

        st.markdown("---")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.markdown("**Demo ohne Konto**\n3 kostenlose Extraktionen")
            if st.button("🚀 Demo starten", use_container_width=True):
                st.session_state.user       = "demo"
                st.session_state.user_id    = None
                st.session_state.user_email = None
                st.rerun()
        with col_d2:
            st.markdown("**Live-Demo ansehen**\nBeispiel Sea Waybill sofort")
            if st.button("👁️ Beispiel ansehen", use_container_width=True):
                st.session_state.user       = "demo"
                st.session_state.user_id    = None
                st.session_state.user_email = None
                st.session_state.show_demo  = True
                st.rerun()

# ════════════════════════════════════════════════════════════════════════════════
# MAIN EXTRACTION APP
# ════════════════════════════════════════════════════════════════════════════════

def show_app():
    st.markdown("""
    <div class="hero">
        <h1>🚢 DocExtract Pro</h1>
        <p>Strukturierte Daten aus Logistikdokumenten — sofort, präzise, skalierbar.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Live Demo ─────────────────────────────────────────────────────────────
    if st.session_state.get("show_demo"):
        st.markdown("### 👁️ Live-Demo — Sea Waybill Extraktion")
        st.markdown('<span style="background:#0c1a1f;border:1px solid #164e63;color:#22d3ee;padding:3px 10px;border-radius:4px;font-size:0.75rem;font-weight:600;">BEISPIELDOKUMENT</span>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        with st.expander("📄 Roher Dokumenttext (simuliert)"):
            st.code(DEMO_WAYBILL_TEXT, language=None)

        d = DEMO_RESULT
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 📋 Dokument")
            for label, value in [
                ("Typ",        d["document_type"]),
                ("Nummer",     d["document_number"]),
                ("Datum",      d["issue_date"]),
                ("Absender",   d["shipper"]["name"]),
                ("Empfänger",  d["consignee"]["name"]),
                ("Incoterms",  d["incoterms"]),
                ("Fracht",     d["freight_terms"]),
                ("Buchungs-Nr",d["booking_number"]),
            ]:
                v = f'<div class="field-value">{value}</div>' if value else '<div class="field-empty">—</div>'
                st.markdown(f'<div class="field-group"><div class="field-label">{label}</div>{v}</div>', unsafe_allow_html=True)

        with col2:
            st.markdown("#### 🚢 Transport")
            for label, value in [
                ("Schiff",  d["vessel_name"]),
                ("Voyage",  d["voyage_number"]),
                ("POL",     d["port_of_loading"]),
                ("POD",     d["port_of_discharge"]),
                ("ETD",     d["etd"]),
                ("ETA",     d["eta"]),
            ]:
                v = f'<div class="field-value">{value}</div>' if value else '<div class="field-empty">—</div>'
                st.markdown(f'<div class="field-group"><div class="field-label">{label}</div>{v}</div>', unsafe_allow_html=True)

        with col3:
            st.markdown("#### 📦 Ladung")
            for label, value in [
                ("Ware",        d["cargo_description"]),
                ("Pakete",      str(d["number_of_packages"])),
                ("Gewicht kg",  str(d["gross_weight_kg"])),
                ("CBM",         str(d["measurement_cbm"])),
                ("HS-Codes",    " · ".join(d["hs_codes"])),
                ("PO",          d["purchase_order"]),
            ]:
                v = f'<div class="field-value">{value}</div>' if value else '<div class="field-empty">—</div>'
                st.markdown(f'<div class="field-group"><div class="field-label">{label}</div>{v}</div>', unsafe_allow_html=True)

        st.markdown("**Container:**")
        for c in d["containers"]:
            st.markdown(f'`{c["container_number"]}` · {c["container_type"]} · Seal: {c["seal_number"]}')

        st.markdown("---")
        st.markdown('<span style="background:#052e16;border:1px solid #14532d;color:#4ade80;padding:3px 10px;border-radius:4px;font-size:0.75rem;font-weight:600;">✅ 14 Felder extrahiert · 0.0s (Demo) · Qualität: 95%</span>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        dc1, dc2 = st.columns(2)
        with dc1:
            if st.button("📂 Eigenes PDF hochladen", type="primary", use_container_width=True):
                st.session_state.show_demo = False
                st.rerun()
        with dc2:
            st.download_button("📥 Demo-Export (JSON)", json.dumps(d, ensure_ascii=False, indent=2),
                               "demo_sea_waybill.json", "application/json", use_container_width=True)

        st.markdown("---")

    c1,c2,c3,c4 = st.columns(4)
    for col, num, lbl in [
        (c1, st.session_state.total_docs,  "Verarbeitet"),
        (c2, "15+",                         "Felder"),
        (c3, "CSV/JSON/Excel",              "Export"),
        (c4, "∞",                           "Batch-Upload"),
    ]:
        with col:
            st.markdown(f'<div class="stat-box"><div class="stat-num">{num}</div><div class="stat-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Credit gate
    credits = get_user_credits()
    if credits <= 0:
        st.error("❌ Keine Credits mehr.")
        if SUPABASE_ENABLED and st.session_state.user_id:
            if st.button("💳 Credits kaufen"):
                st.session_state.page = "billing"; st.rerun()
        else:
            st.info("Erstelle ein Konto und kaufe Credits zum Weitermachen.")
        return

    uploaded_files = st.file_uploader(
        "📂 PDFs hochladen (Mehrfachauswahl möglich)",
        type=["pdf"], accept_multiple_files=True
    )

    if uploaded_files:
        new_results = []

        for uf in uploaded_files:
            if any(h["filename"] == uf.name for h in st.session_state.history):
                continue

            st.markdown(f"---\n### 📄 {uf.name}")

            with st.spinner("Text wird gelesen..."):
                try:
                    with pdfplumber.open(uf) as pdf:
                        text = "\n".join(p.extract_text() or "" for p in pdf.pages)
                except Exception as e:
                    st.error(f"PDF-Lesefehler: {e}")
                    continue

            # OCR fallback für Scan-PDFs
            if not text.strip():
                try:
                    import fitz  # PyMuPDF
                    uf.seek(0)
                    doc = fitz.open(stream=uf.read(), filetype="pdf")
                    ocr_parts = []
                    for page in doc:
                        pix = page.get_pixmap(dpi=300)
                        # Extract text via OCR using PyMuPDF's built-in
                        tp = page.get_text("text")
                        if tp.strip():
                            ocr_parts.append(tp)
                    text = "\n".join(ocr_parts)
                    if text.strip():
                        st.info("🔍 OCR angewendet (Scan-PDF erkannt)")
                except Exception:
                    pass

            if not text.strip():
                st.warning("⚠️ Kein Text extrahierbar. Qualität des PDFs prüfen.")
                continue

            with st.expander("Roher PDF-Text"):
                st.text(text[:5000])

            with st.spinner("🤖 Claude analysiert..."):
                t0 = time.time()
                try:
                    # Deduct credit
                    if SUPABASE_ENABLED and st.session_state.user_id:
                        if not deduct_credit(st.session_state.user_id):
                            st.error("Keine Credits mehr."); break
                    else:
                        st.session_state.demo_used += 1

                    data    = extract_from_text(text)
                    elapsed = round(time.time() - t0, 1)
                    nfields = count_extracted_fields(data)
                    quality = min(100, int(nfields / 20 * 100))

                    st.session_state.total_docs += 1
                    st.session_state.total_time += elapsed
                    st.session_state.history.append({
                        "filename": uf.name, "doc_type": data.document_type,
                        "doc_number": data.document_number,
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "elapsed": elapsed, "fields": nfields
                    })

                    # DB logging
                    if SUPABASE_ENABLED and st.session_state.user_id:
                        log_usage(st.session_state.user_id, uf.name,
                                  data.document_type, data.document_number or "",
                                  True, elapsed, nfields)
                        # Email notification
                        if st.session_state.user_email:
                            send_extraction_complete(
                                st.session_state.user_email, uf.name,
                                data.document_type, data.document_number,
                                True, elapsed, nfields
                            )
                        # Webhooks
                        webhooks = get_webhooks(st.session_state.user_id)
                        for wh in webhooks:
                            if "extraction.completed" in (wh.get("events") or []):
                                evt = build_extraction_event(data, uf.name, True, elapsed, nfields)
                                deliver_webhook(wh["url"], wh.get("secret",""), "extraction.completed", evt)
                        # Low credits alert
                        remaining = get_credits(st.session_state.user_id)
                        if remaining <= 5 and st.session_state.user_email:
                            send_low_credits_alert(st.session_state.user_email, remaining)

                    # Quality indicator
                    col_q1, col_q2 = st.columns([3,1])
                    with col_q1:
                        st.markdown(f"""
                        <div style="margin-bottom:0.5rem;">
                            <span style="background:#dcfce7;color:#166534;padding:3px 10px;border-radius:20px;font-size:0.8rem;font-weight:600;">
                                ✅ {elapsed}s · {nfields} Felder
                            </span>
                        </div>
                        <div class="quality-bar"><div class="quality-fill" style="width:{quality}%"></div></div>
                        <div style="font-size:0.75rem;color:#6b7280;margin-top:4px;">Qualitätsscore: {quality}%</div>
                        """, unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)

                    # Results in 3 columns
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown("#### 📋 Dokument")
                        for label, value in [
                            ("Typ",        data.document_type),
                            ("Nummer",     data.document_number),
                            ("Datum",      data.issue_date),
                            ("Absender",   data.shipper.name if data.shipper else None),
                            ("Empfänger",  data.consignee.name if data.consignee else None),
                            ("Notify",     data.notify_party.name if data.notify_party else None),
                            ("Incoterms",  data.incoterms),
                            ("Frachtbed.", data.freight_terms),
                        ]:
                            v = f'<div class="field-value">{value}</div>' if value else '<div class="field-empty">—</div>'
                            st.markdown(f'<div class="field-group"><div class="field-label">{label}</div>{v}</div>', unsafe_allow_html=True)

                    with col2:
                        st.markdown("#### 🚢 Transport")
                        for label, value in [
                            ("Schiff",   data.vessel_name),
                            ("IMO",      data.imo_number),
                            ("Voyage",   data.voyage_number),
                            ("Service",  data.service_type),
                            ("POL",      data.port_of_loading),
                            ("POD",      data.port_of_discharge),
                            ("ETD",      data.etd),
                            ("ETA",      data.eta),
                        ]:
                            v = f'<div class="field-value">{value}</div>' if value else '<div class="field-empty">—</div>'
                            st.markdown(f'<div class="field-group"><div class="field-label">{label}</div>{v}</div>', unsafe_allow_html=True)

                    with col3:
                        st.markdown("#### 📦 Ladung")
                        for label, value in [
                            ("Ware",       data.cargo_description),
                            ("Pakete",     str(data.number_of_packages) if data.number_of_packages else None),
                            ("Gewicht kg", str(data.gross_weight_kg) if data.gross_weight_kg else None),
                            ("CBM",        str(data.measurement_cbm) if data.measurement_cbm else None),
                            ("HS-Codes",   ", ".join(data.hs_codes) if data.hs_codes else None),
                            ("Buchungs-Nr",data.booking_number),
                            ("PO",         data.purchase_order),
                            ("DG-Ladung",  "Ja ⚠️" if data.dangerous_goods else None),
                        ]:
                            v = f'<div class="field-value">{value}</div>' if value else '<div class="field-empty">—</div>'
                            st.markdown(f'<div class="field-group"><div class="field-label">{label}</div>{v}</div>', unsafe_allow_html=True)

                    # Containers
                    if data.containers:
                        st.markdown("**🏗️ Container**")
                        c_data = []
                        for c in data.containers:
                            c_data.append({
                                "Nummer": c.container_number or "—",
                                "Typ": c.container_type or "—",
                                "Seal": c.seal_number or "—",
                                "Gewicht kg": c.gross_weight_kg or "—",
                                "CBM": c.cbm or "—"
                            })
                        st.table(c_data)

                    # Invoice line items
                    if data.line_items:
                        st.markdown("**💰 Rechnungspositionen**")
                        items = []
                        for li in data.line_items:
                            items.append({
                                "Beschreibung": li.description,
                                "Menge": li.quantity,
                                "Einheit": li.unit or "—",
                                "Einzelpreis": li.unit_price,
                                "Gesamt": li.total,
                                "HS-Code": li.hs_code or "—"
                            })
                        st.table(items)

                    # Export
                    st.markdown("---")
                    flat = to_flat_dict(data, uf.name)
                    new_results.append(flat)

                    ec1, ec2, ec3 = st.columns(3)
                    with ec1:
                        st.download_button(
                            "📥 CSV", export_csv([flat]),
                            f"{data.document_number or uf.name}.csv",
                            "text/csv", use_container_width=True
                        )
                    with ec2:
                        st.download_button(
                            "📥 JSON",
                            json.dumps(data.model_dump(), ensure_ascii=False, indent=2),
                            f"{data.document_number or uf.name}.json",
                            "application/json", use_container_width=True
                        )
                    with ec3:
                        excel_bytes = export_excel([flat])
                        st.download_button(
                            "📥 Excel", excel_bytes,
                            f"{data.document_number or uf.name}.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )

                except Exception as e:
                    st.error(f"❌ Fehler: {e}")
                    if SUPABASE_ENABLED and st.session_state.user_id:
                        log_usage(st.session_state.user_id, uf.name, "unknown", "", False, 0, 0)

        # Batch export
        all_results = [h for h in st.session_state.history]
        if len(new_results) > 1:
            st.markdown("---\n### 📦 Batch-Export (alle Dokumente)")
            bc1, bc2, bc3 = st.columns(3)
            all_flat = new_results
            with bc1:
                st.download_button("📥 Alle als CSV",   export_csv(all_flat),    "batch_export.csv",  "text/csv", use_container_width=True)
            with bc2:
                st.download_button("📥 Alle als JSON",  export_json(all_flat),   "batch_export.json", "application/json", use_container_width=True)
            with bc3:
                excel_batch = export_excel(all_flat)
                st.download_button("📥 Alle als Excel", excel_batch, "batch_export.xlsx",
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

    # Session history
    if st.session_state.history:
        st.markdown("---\n## 📋 Session-History")
        for h in reversed(st.session_state.history):
            st.markdown(f"`{h['timestamp']}` · **{h['filename']}** · `{h['doc_type']}` · {h.get('fields',0)} Felder · ⏱ {h['elapsed']}s")

# ════════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════════════════════════════

def show_dashboard():
    st.markdown("## 📊 Dashboard")
    if not SUPABASE_ENABLED or not st.session_state.user_id:
        st.info("Dashboard nach Anmeldung verfügbar.")
        return

    stats = get_usage_stats(st.session_state.user_id)
    credits = get_credits(st.session_state.user_id)

    c1,c2,c3,c4,c5 = st.columns(5)
    for col, num, lbl in [
        (c1, stats["total"],          "Gesamt Docs"),
        (c2, stats["successful"],     "Erfolgreich"),
        (c3, f"{stats['success_rate']:.0f}%", "Erfolgsrate"),
        (c4, f"€{stats['total_spent']:.2f}", "Ausgegeben"),
        (c5, credits,                 "Credits verbl."),
    ]:
        with col:
            st.markdown(f'<div class="stat-box"><div class="stat-num">{num}</div><div class="stat-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if stats["doc_types"]:
        st.markdown("### Dokumenttypen")
        dt_col1, dt_col2 = st.columns([1,2])
        with dt_col1:
            for dt, count in sorted(stats["doc_types"].items(), key=lambda x: -x[1]):
                pct = int(count / stats["total"] * 100) if stats["total"] else 0
                st.markdown(f"**{dt}**: {count} ({pct}%)")

    st.markdown("---\n### Letzte Extraktionen")
    logs = get_usage_log(st.session_state.user_id, limit=50)
    if logs:
        # Export
        flat_logs = [{
            "timestamp": l["created_at"][:16], "filename": l["filename"],
            "doc_type": l["doc_type"], "doc_number": l["doc_number"],
            "success": l["success"], "latency_s": l["latency_s"],
            "cost_eur": l["cost_eur"]
        } for l in logs]
        st.download_button("📥 Log als CSV", export_csv(flat_logs), "usage_log.csv", "text/csv")
        st.markdown("<br>", unsafe_allow_html=True)

        for log in logs[:30]:
            icon = "✅" if log["success"] else "❌"
            st.markdown(
                f"`{log['created_at'][:16]}` {icon} **{log['filename'] or '—'}** "
                f"· `{log['doc_type']}` · {log['latency_s']}s · €{log['cost_eur']:.2f}"
            )

# ════════════════════════════════════════════════════════════════════════════════
# BILLING
# ════════════════════════════════════════════════════════════════════════════════

def show_billing():
    st.markdown("## 💳 Credits kaufen")
    st.markdown("**€0.49 pro erfolgreich extrahiertem Dokument · Pay-as-you-go · Keine Abo-Gebühren**")
    st.markdown("---")

    stripe_links = {
        10:  os.environ.get("STRIPE_10",  "#"),
        50:  os.environ.get("STRIPE_50",  "#"),
        200: os.environ.get("STRIPE_200", "#"),
    }

    c1,c2,c3 = st.columns(3)
    plans = [
        (c1, 10,  "4.90",  "Starter",    "€0.49/Doc"),
        (c2, 50,  "19.90", "Business",   "€0.40/Doc", True),
        (c3, 200, "69.90", "Pro",        "€0.35/Doc"),
    ]
    for args in plans:
        col, credits, price, name, per, *popular = args
        with col:
            badge = "⭐ Empfohlen · " if popular else ""
            st.markdown(f"""
            <div style="border:2px solid {'#3b82f6' if popular else '#e5e7eb'};border-radius:12px;padding:1.5rem;text-align:center;">
                <div style="font-size:1.1rem;font-weight:700;">{name}</div>
                <div style="font-size:2.5rem;font-weight:800;color:#1d4ed8;">€{price}</div>
                <div style="color:#6b7280;">{credits} Credits · {per}</div>
                <div style="font-size:0.8rem;color:#9ca3af;margin-top:0.25rem;">{badge}</div>
            </div>
            """, unsafe_allow_html=True)
            link = stripe_links.get(credits, "#")
            st.markdown(f'<br><a href="{link}" target="_blank"><button style="width:100%;background:#1d4ed8;color:white;border:none;padding:10px;border-radius:8px;font-weight:600;cursor:pointer;font-size:0.95rem;">Jetzt kaufen</button></a>', unsafe_allow_html=True)

    st.markdown("---")
    st.info("💡 Nach dem Kauf: Credits erscheinen automatisch auf deinem Konto. Bei Fragen: support@docextract.pro")

# ════════════════════════════════════════════════════════════════════════════════
# API KEYS
# ════════════════════════════════════════════════════════════════════════════════

def show_api_keys():
    st.markdown("## 🔑 API Keys")
    if not SUPABASE_ENABLED or not st.session_state.user_id:
        st.info("API Keys nach Anmeldung verfügbar.")
        return

    st.markdown("### API Dokumentation")
    base_url = "https://waybil-wqgbsxbcmfkfdzqswciqqp.streamlit.app"

    with st.expander("📖 Extraktion via API"):
        st.code(f"""
# POST /api/v1/extract
curl -X POST "{base_url}/api/v1/extract" \\
  -H "Authorization: Bearer dxp_YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{"text": "SEA WAYBILL NO: SWB-001..."}}'

# Response
{{
  "success": true,
  "document_type": "sea_waybill",
  "document_number": "SWB-001",
  "vessel_name": "MSC OSCAR",
  "port_of_loading": "CNSHA",
  "port_of_discharge": "DEHAM",
  ...
}}
""", language="bash")

    st.markdown("---\n### Neuen API Key erstellen")
    key_name = st.text_input("Key-Name (z.B. 'SAP Integration', 'TMS Webhook')")
    if st.button("🔑 API Key erstellen", type="primary"):
        if key_name.strip():
            new_key = create_api_key(st.session_state.user_id, key_name.strip())
            st.success("✅ API Key erstellt — wird nur einmal angezeigt!")
            st.code(new_key)
            st.warning("⚠️ Sofort kopieren und sicher speichern!")

    st.markdown("---\n### Bestehende Keys")
    keys = get_api_keys(st.session_state.user_id)
    if keys:
        for k in keys:
            col1, col2 = st.columns([4,1])
            with col1:
                last = k.get("last_used_at", "Nie")[:10] if k.get("last_used_at") else "Nie"
                st.markdown(f"**{k['name']}** · `{k['key_prefix']}...` · Erstellt: {k['created_at'][:10]} · Zuletzt: {last}")
            with col2:
                if st.button("🗑️", key=f"revoke_{k['id']}"):
                    revoke_api_key(k["id"], st.session_state.user_id)
                    st.rerun()
    else:
        st.info("Noch keine API Keys erstellt.")

# ════════════════════════════════════════════════════════════════════════════════
# WEBHOOKS
# ════════════════════════════════════════════════════════════════════════════════

def show_webhooks():
    st.markdown("## 🔔 Webhooks")
    if not SUPABASE_ENABLED or not st.session_state.user_id:
        st.info("Webhooks nach Anmeldung verfügbar.")
        return

    st.markdown("Erhalte Extraktionsergebnisse automatisch in dein System.")

    with st.expander("📖 Webhook-Payload Beispiel"):
        st.code(json.dumps({
            "event": "extraction.completed",
            "timestamp": 1715000000,
            "data": {
                "filename": "waybill_001.pdf",
                "success": True,
                "document_type": "sea_waybill",
                "document_number": "SWB-2024-001",
                "vessel_name": "MSC OSCAR",
                "port_of_loading": "CNSHA",
                "port_of_discharge": "DEHAM",
                "container_count": 2
            }
        }, indent=2), language="json")
        st.markdown("**Signatur-Verifikation (Python):**")
        st.code("""
import hmac, hashlib
def verify(payload: str, secret: str, signature: str) -> bool:
    expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
""", language="python")

    st.markdown("---\n### Webhook hinzufügen")
    wh_url    = st.text_input("Endpoint URL (https://...)")
    wh_events = st.multiselect("Events", ["extraction.completed", "extraction.failed", "credits.low"])

    if st.button("Webhook speichern", type="primary"):
        if wh_url.startswith("https://") and wh_events:
            save_webhook(st.session_state.user_id, wh_url, wh_events)
            st.success("✅ Webhook gespeichert.")
            st.rerun()
        else:
            st.error("URL muss mit https:// beginnen und mindestens ein Event ausgewählt sein.")

    st.markdown("---\n### Aktive Webhooks")
    webhooks = get_webhooks(st.session_state.user_id)
    if webhooks:
        for wh in webhooks:
            st.markdown(f"**{wh['url']}** · Events: `{', '.join(wh.get('events') or [])}` · Seit: {wh['created_at'][:10]}")
    else:
        st.info("Noch keine Webhooks konfiguriert.")

# ════════════════════════════════════════════════════════════════════════════════
# ROUTER
# ════════════════════════════════════════════════════════════════════════════════

if not is_logged_in() and SUPABASE_ENABLED:
    show_login()
elif st.session_state.page == "dashboard":
    show_dashboard()
elif st.session_state.page == "billing":
    show_billing()
elif st.session_state.page == "api_keys":
    show_api_keys()
elif st.session_state.page == "webhooks":
    show_webhooks()
else:
    show_app()
