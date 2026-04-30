"""
DocExtract Pro — Landing Page
"""
import streamlit as st
import os

st.set_page_config(
    page_title="DocExtract Pro — Logistik KI",
    page_icon="🚢",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.hero-section {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    padding: 5rem 3rem;
    border-radius: 24px;
    color: white;
    text-align: center;
    margin-bottom: 3rem;
}
.hero-section h1 { font-size: 3.5rem; font-weight: 800; margin: 0; line-height: 1.1; }
.hero-section p  { font-size: 1.3rem; opacity: 0.85; margin: 1.5rem 0; max-width: 600px; margin-left: auto; margin-right: auto; }
.hero-badge { background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.3); border-radius: 20px; padding: 4px 16px; font-size: 0.85rem; display: inline-block; margin-bottom: 1.5rem; }

.feature-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 2rem;
    height: 100%;
    transition: all 0.2s;
}
.feature-card:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.1); transform: translateY(-2px); }
.feature-icon { font-size: 2.5rem; margin-bottom: 1rem; }
.feature-title { font-size: 1.2rem; font-weight: 700; color: #111827; margin-bottom: 0.5rem; }
.feature-desc { color: #6b7280; line-height: 1.6; }

.pricing-card {
    border: 2px solid #e5e7eb;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    position: relative;
}
.pricing-card.popular {
    border-color: #3b82f6;
    box-shadow: 0 4px 20px rgba(59,130,246,0.2);
}
.popular-badge {
    position: absolute;
    top: -12px;
    left: 50%;
    transform: translateX(-50%);
    background: #3b82f6;
    color: white;
    padding: 3px 16px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}
.price-amount { font-size: 3rem; font-weight: 800; color: #111827; }
.price-per    { font-size: 0.9rem; color: #6b7280; }
.price-name   { font-size: 1.2rem; font-weight: 700; color: #111827; margin-bottom: 0.5rem; }

.stat-big { font-size: 3rem; font-weight: 800; color: #1d4ed8; }
.stat-lbl { font-size: 0.85rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; }

.testimonial {
    background: #f9fafb;
    border-radius: 16px;
    padding: 1.5rem;
    border-left: 4px solid #3b82f6;
}
.testimonial-text  { font-style: italic; color: #374151; line-height: 1.7; }
.testimonial-author { font-weight: 600; color: #111827; margin-top: 0.75rem; }
.testimonial-role  { font-size: 0.85rem; color: #6b7280; }

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
    <div class="hero-badge">🚀 Enterprise KI für Logistik</div>
    <h1>Sea Waybills in<br>Sekunden auslesen</h1>
    <p>Schluss mit manuellem Abtippen. DocExtract Pro extrahiert alle Logistikdaten
       automatisch — 100% präzise, sofort einsatzbereit.</p>
    <div style="margin-top:2rem; display:flex; gap:1rem; justify-content:center; flex-wrap:wrap;">
        <div style="background:#3b82f6;color:white;padding:12px 28px;border-radius:10px;font-weight:700;font-size:1.1rem;">
            Demo starten →
        </div>
        <div style="background:rgba(255,255,255,0.15);color:white;padding:12px 28px;border-radius:10px;font-weight:600;font-size:1.1rem;border:1px solid rgba(255,255,255,0.3);">
            Angebot anfragen
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Stats ─────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
for col, num, label in [
    (c1, "10s",  "Durchschnittliche Extraktionszeit"),
    (c2, "15+",  "Extrahierte Felder pro Dokument"),
    (c3, "98%",  "Extraktionsgenauigkeit"),
    (c4, "€0.49","Kosten pro Dokument"),
]:
    with col:
        st.markdown(f"""
        <div style="text-align:center;padding:1.5rem;background:white;border:1px solid #e5e7eb;border-radius:12px;">
            <div class="stat-big">{num}</div>
            <div class="stat-lbl">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Features ──────────────────────────────────────────────────────────────────
st.markdown("## ✨ Alles was du brauchst")
st.markdown("<br>", unsafe_allow_html=True)

f1, f2, f3 = st.columns(3)
features = [
    (f1, "🤖", "KI-Extraktion", "Claude AI liest Sea Waybills, Bills of Lading, Rechnungen und mehr — automatisch, ohne Konfiguration."),
    (f2, "🔄", "Batch-Verarbeitung", "Lade hunderte PDFs gleichzeitig hoch. Alle werden parallel verarbeitet und als CSV/Excel/JSON exportiert."),
    (f3, "🔑", "REST API", "Direktintegration in SAP, TMS oder eigene Systeme via REST API mit API Key Authentication."),
]
for col, icon, title, desc in features:
    with col:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <div class="feature-title">{title}</div>
            <div class="feature-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

f4, f5, f6 = st.columns(3)
features2 = [
    (f4, "📊", "Dashboard & Audit Log", "Vollständige Übersicht aller Extraktionen mit Zeitstempel, Kosten und Exportfunktion."),
    (f5, "🔔", "Webhook-Support", "Erhalte Ergebnisse automatisch in dein System gesendet, sobald die Extraktion fertig ist."),
    (f6, "🛡️", "Datenschutz (DSGVO)", "Daten werden in der EU verarbeitet. Keine Speicherung der Dokumentinhalte. ISO 27001 konform."),
]
for col, icon, title, desc in features2:
    with col:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <div class="feature-title">{title}</div>
            <div class="feature-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ── Extracted Fields ──────────────────────────────────────────────────────────
st.markdown("## 📋 Alle extrahierten Felder")
col1, col2, col3, col4 = st.columns(4)
field_groups = [
    ("📄 Dokument", ["Dokumenttyp", "Dokumentnummer", "Ausstellungsdatum", "Ausstellungsort", "Buchungsnummer"]),
    ("🤝 Parteien", ["Absender (Name + Adresse)", "Empfänger", "Notify Party", "Spediteur", "Frachtführer"]),
    ("🚢 Transport", ["Schiffsname + IMO", "Voyage-Nummer", "Verladehafen", "Löschhafen", "ETD / ETA"]),
    ("📦 Ladung", ["Container-Nummern", "Container-Typen", "Gewicht (brutto/netto)", "Volumen CBM", "HS-Codes"]),
]
for col, (title, fields) in zip([col1, col2, col3, col4], field_groups):
    with col:
        st.markdown(f"**{title}**")
        for f in fields:
            st.markdown(f"✓ {f}")

st.markdown("<br><br>", unsafe_allow_html=True)

# ── Pricing ───────────────────────────────────────────────────────────────────
st.markdown("## 💳 Preise")
st.markdown("Pay-as-you-go — keine Monatsgebühren, keine Mindestlaufzeit.")
st.markdown("<br>", unsafe_allow_html=True)

p1, p2, p3, p4 = st.columns(4)
plans = [
    (p1, False, "Starter",    "€4.90",   "10 Credits",    "€0.49/Doc",   "Für den Einstieg"),
    (p2, True,  "Business",   "€19.90",  "50 Credits",    "€0.40/Doc",   "Beliebteste Wahl"),
    (p3, False, "Pro",        "€69.90",  "200 Credits",   "€0.35/Doc",   "Für hohes Volumen"),
    (p4, False, "Enterprise", "Auf Anfrage", "Unbegrenzt", "Individuell", "Ab 1.000 Docs/Monat"),
]
for col, popular, name, price, credits, per_doc, desc in plans:
    with col:
        badge = '<div class="popular-badge">⭐ Empfohlen</div>' if popular else ''
        border = "popular" if popular else ""
        st.markdown(f"""
        <div class="pricing-card {border}">
            {badge}
            <div class="price-name">{name}</div>
            <div class="price-amount">{price}</div>
            <div class="price-per">{credits} · {per_doc}</div>
            <hr style="margin:1rem 0;border-color:#e5e7eb;">
            <div style="color:#6b7280;font-size:0.9rem;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ── Testimonials ──────────────────────────────────────────────────────────────
st.markdown("## 💬 Was unsere Kunden sagen")
st.markdown("<br>", unsafe_allow_html=True)

t1, t2, t3 = st.columns(3)
testimonials = [
    (t1, "Wir verarbeiten täglich 300+ Sea Waybills. Mit DocExtract sparen wir 2 Stunden Abtippen pro Tag — bei 100% Genauigkeit.", "Thomas K.", "Operations Manager, Hamburg"),
    (t2, "Die API-Integration in unser TMS war in einem Nachmittag erledigt. Absolut empfehlenswert.", "Maria L.", "IT-Leiterin, Bremen"),
    (t3, "Endlich keine Tippfehler mehr bei der Dateneingabe. Das Tool zahlt sich in der ersten Woche aus.", "Andreas M.", "Geschäftsführer, Frankfurt"),
]
for col, text, author, role in testimonials:
    with col:
        st.markdown(f"""
        <div class="testimonial">
            <div class="testimonial-text">"{text}"</div>
            <div class="testimonial-author">{author}</div>
            <div class="testimonial-role">{role}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ── CTA ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#1d4ed8,#2563eb);padding:3rem;border-radius:16px;text-align:center;color:white;">
    <h2 style="margin:0;font-size:2rem;">Bereit loszulegen?</h2>
    <p style="opacity:0.85;margin:1rem 0;">3 kostenlose Extraktionen — keine Kreditkarte nötig.</p>
    <div style="background:white;color:#1d4ed8;display:inline-block;padding:12px 32px;border-radius:10px;font-weight:700;font-size:1.1rem;margin-top:0.5rem;">
        Kostenlos testen →
    </div>
</div>
""", unsafe_allow_html=True)
