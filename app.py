import streamlit as st
import pdfplumber
import json
import csv
import io
import time
from datetime import datetime
from extractor import extract_from_text

st.set_page_config(
    page_title="DocExtract Pro — Logistik KI",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .hero {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
    }
    .hero h1 { margin: 0; font-size: 2.2rem; font-weight: 700; }
    .hero p  { margin: 0.5rem 0 0; opacity: 0.8; font-size: 1.1rem; }

    .stat-box {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stat-num  { font-size: 2rem; font-weight: 700; color: #1d4ed8; }
    .stat-label{ font-size: 0.8rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; }

    .result-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .field-group { margin-bottom: 0.9rem; }
    .field-label { font-size: 0.72rem; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.06em; }
    .field-value { font-size: 0.97rem; font-weight: 500; color: #111827; margin-top: 2px; }
    .field-empty { font-size: 0.97rem; color: #d1d5db; }

    .badge-success { background:#dcfce7; color:#166534; padding:3px 10px; border-radius:20px; font-size:0.8rem; font-weight:600; }
    .badge-warn    { background:#fef9c3; color:#854d0e; padding:3px 10px; border-radius:20px; font-size:0.8rem; font-weight:600; }

    .section-title { font-size:1.1rem; font-weight:700; color:#111827; margin-bottom:0.8rem; display:flex; align-items:center; gap:0.4rem; }

    div[data-testid="stFileUploader"] { border: 2px dashed #3b82f6; border-radius: 12px; padding: 1rem; background: #eff6ff; }

    .stButton > button {
        background: linear-gradient(135deg, #1d4ed8, #2563eb);
        color: white; border: none; border-radius: 8px;
        font-weight: 600; padding: 0.6rem 1.5rem;
        transition: all 0.2s;
    }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(37,99,235,0.4); }

    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "total_docs" not in st.session_state:
    st.session_state.total_docs = 0
if "total_time" not in st.session_state:
    st.session_state.total_time = 0.0

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚢 DocExtract Pro")
    st.markdown("*Enterprise Logistik-KI*")
    st.divider()

    st.markdown("**Unterstützte Dokumente**")
    for doc in ["Sea Waybills", "Bills of Lading", "Commercial Invoices", "Packing Lists", "Certificates of Origin"]:
        st.markdown(f"✓ {doc}")
    st.divider()

    st.markdown("**Extraktionsfelder**")
    for f in ["Absender / Empfänger", "Schiff & Voyage", "Container-Nummern", "Häfen & Daten", "Gewicht & Volumen", "HS-Codes", "Frachtbedingungen"]:
        st.markdown(f"• {f}")
    st.divider()

    if st.session_state.total_docs > 0:
        avg = st.session_state.total_time / st.session_state.total_docs
        st.metric("Dokumente verarbeitet", st.session_state.total_docs)
        st.metric("Ø Extraktionszeit", f"{avg:.1f}s")

    st.divider()
    st.caption("Powered by Claude AI · v2.0")

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🚢 DocExtract Pro</h1>
    <p>Logistikdokumente in Sekunden auslesen — kein manuelles Abtippen, 0 Fehler.</p>
</div>
""", unsafe_allow_html=True)

# ── Stats ─────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="stat-box"><div class="stat-num">{st.session_state.total_docs}</div><div class="stat-label">Verarbeitet</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="stat-box"><div class="stat-num">15+</div><div class="stat-label">Felder extrahiert</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="stat-box"><div class="stat-num">CSV</div><div class="stat-label">& JSON Export</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown('<div class="stat-box"><div class="stat-num">∞</div><div class="stat-label">Batch-Upload</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Upload ────────────────────────────────────────────────────────────────────
uploaded_files = st.file_uploader(
    "📂 PDFs hochladen (Mehrfachauswahl möglich)",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        already = any(h["filename"] == uploaded_file.name for h in st.session_state.history)
        if already:
            continue

        st.markdown(f"---\n### 📄 {uploaded_file.name}")

        with st.spinner("Text wird gelesen..."):
            with pdfplumber.open(uploaded_file) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)

        if not text.strip():
            st.warning("⚠️ Kein Text gefunden — Scan-PDF ohne OCR.")
            continue

        with st.expander("Roher PDF-Text"):
            st.text(text[:4000])

        # Auto-extract
        with st.spinner("🤖 KI analysiert Dokument..."):
            t0 = time.time()
            try:
                data = extract_from_text(text)
                elapsed = round(time.time() - t0, 1)

                st.session_state.total_docs += 1
                st.session_state.total_time += elapsed
                st.session_state.history.append({
                    "filename": uploaded_file.name,
                    "doc_type": data.document_type,
                    "doc_number": data.document_number,
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "elapsed": elapsed,
                    "data": data
                })

                st.markdown(f'<span class="badge-success">✅ Extraktion erfolgreich — {elapsed}s</span>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown('<div class="section-title">📋 Dokument</div>', unsafe_allow_html=True)
                    for label, value in [
                        ("Typ", data.document_type),
                        ("Nummer", data.document_number),
                        ("Absender", data.shipper),
                        ("Empfänger", data.consignee),
                        ("Notify Party", data.notify_party),
                    ]:
                        v = value or None
                        val_html = f'<div class="field-value">{v}</div>' if v else '<div class="field-empty">—</div>'
                        st.markdown(f'<div class="field-group"><div class="field-label">{label}</div>{val_html}</div>', unsafe_allow_html=True)

                with col2:
                    st.markdown('<div class="section-title">🚢 Transport</div>', unsafe_allow_html=True)
                    for label, value in [
                        ("Schiff", data.vessel_name),
                        ("Voyage", data.voyage_number),
                        ("Verladehafen", data.port_of_loading),
                        ("Löschhafen", data.port_of_discharge),
                        ("ETD", data.etd),
                        ("ETA", data.eta),
                    ]:
                        v = value or None
                        val_html = f'<div class="field-value">{v}</div>' if v else '<div class="field-empty">—</div>'
                        st.markdown(f'<div class="field-group"><div class="field-label">{label}</div>{val_html}</div>', unsafe_allow_html=True)

                with col3:
                    st.markdown('<div class="section-title">📦 Ladung</div>', unsafe_allow_html=True)
                    for label, value in [
                        ("Warenbeschreibung", data.cargo_description),
                        ("Gewicht (kg)", str(data.gross_weight_kg) if data.gross_weight_kg else None),
                        ("Volumen (CBM)", str(data.measurement_cbm) if data.measurement_cbm else None),
                        ("Frachtbedingungen", data.freight_terms),
                        ("HS-Codes", ", ".join(data.hs_codes) if data.hs_codes else None),
                    ]:
                        val_html = f'<div class="field-value">{value}</div>' if value else '<div class="field-empty">—</div>'
                        st.markdown(f'<div class="field-group"><div class="field-label">{label}</div>{val_html}</div>', unsafe_allow_html=True)

                if data.containers:
                    st.markdown("**🏗️ Container**")
                    for i, c in enumerate(data.containers, 1):
                        st.markdown(f"`{c.container_number or '?'}` · {c.container_type or '—'} · Seal: {c.seal_number or '—'}")

                # ── Export ────────────────────────────────────────────────────
                st.markdown("---")
                flat = data.model_dump()
                flat["containers"] = json.dumps(flat["containers"], ensure_ascii=False)
                flat["hs_codes"] = ", ".join(flat["hs_codes"])

                buf_csv = io.StringIO()
                writer = csv.DictWriter(buf_csv, fieldnames=flat.keys())
                writer.writeheader()
                writer.writerow(flat)

                ec1, ec2 = st.columns(2)
                with ec1:
                    st.download_button(
                        "📥 CSV exportieren",
                        buf_csv.getvalue(),
                        f"{data.document_number or uploaded_file.name}.csv",
                        "text/csv",
                        use_container_width=True
                    )
                with ec2:
                    st.download_button(
                        "📥 JSON exportieren",
                        json.dumps(data.model_dump(), ensure_ascii=False, indent=2),
                        f"{data.document_number or uploaded_file.name}.json",
                        "application/json",
                        use_container_width=True
                    )

            except Exception as e:
                st.error(f"❌ Fehler: {e}")

# ── History ───────────────────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown("---")
    st.markdown("## 📊 Verarbeitete Dokumente (diese Session)")
    for h in reversed(st.session_state.history):
        st.markdown(
            f"`{h['timestamp']}` &nbsp; **{h['filename']}** &nbsp; "
            f"· Typ: `{h['doc_type']}` · Nr: `{h['doc_number'] or '—'}` · ⏱ {h['elapsed']}s",
            unsafe_allow_html=True
        )
