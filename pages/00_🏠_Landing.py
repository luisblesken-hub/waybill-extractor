"""
DocExtract Pro — Enterprise Landing Page
Design: Dark professional, inspired by Vercel / Linear
"""
import streamlit as st

st.set_page_config(
    page_title="DocExtract Pro — Logistics AI",
    page_icon="🚢",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stToolbar"] { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }

body { background: #09090b; color: #fafafa; }

/* ── NAV ─────────────────────────────── */
.nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.25rem 4rem;
    border-bottom: 1px solid #1f1f23;
    background: rgba(9,9,11,0.8);
    backdrop-filter: blur(20px);
    position: sticky;
    top: 0;
    z-index: 100;
}
.nav-logo { font-size: 1.1rem; font-weight: 700; color: #fafafa; letter-spacing: -0.02em; }
.nav-links { display: flex; gap: 2.5rem; }
.nav-links a { color: #a1a1aa; font-size: 0.875rem; text-decoration: none; transition: color 0.15s; }
.nav-links a:hover { color: #fafafa; }
.nav-cta {
    background: #fafafa; color: #09090b;
    padding: 0.5rem 1.25rem; border-radius: 6px;
    font-size: 0.875rem; font-weight: 600;
    cursor: pointer; border: none;
    transition: background 0.15s;
}

/* ── HERO ────────────────────────────── */
.hero-wrap {
    padding: 7rem 4rem 5rem;
    text-align: center;
    max-width: 900px;
    margin: 0 auto;
}
.hero-badge {
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: #18181b; border: 1px solid #27272a;
    border-radius: 100px; padding: 0.35rem 1rem;
    font-size: 0.8rem; color: #a1a1aa;
    margin-bottom: 2rem;
}
.hero-badge span { color: #22d3ee; font-weight: 600; }
.hero-h1 {
    font-size: clamp(2.5rem, 5vw, 4rem);
    font-weight: 800;
    line-height: 1.05;
    letter-spacing: -0.04em;
    color: #fafafa;
    margin: 0 0 1.5rem;
}
.hero-h1 em { font-style: normal; color: #22d3ee; }
.hero-sub {
    font-size: 1.2rem;
    color: #71717a;
    max-width: 560px;
    margin: 0 auto 2.5rem;
    line-height: 1.7;
    font-weight: 400;
}
.hero-actions {
    display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;
}
.btn-primary {
    background: #fafafa; color: #09090b;
    padding: 0.75rem 2rem; border-radius: 8px;
    font-size: 0.95rem; font-weight: 600;
    cursor: pointer; border: none;
    transition: all 0.15s;
    text-decoration: none;
}
.btn-secondary {
    background: transparent; color: #fafafa;
    padding: 0.75rem 2rem; border-radius: 8px;
    font-size: 0.95rem; font-weight: 500;
    cursor: pointer;
    border: 1px solid #27272a;
    transition: all 0.15s;
    text-decoration: none;
}
.btn-secondary:hover { border-color: #52525b; }

/* ── STATS BAR ───────────────────────── */
.stats-bar {
    display: flex;
    justify-content: center;
    gap: 0;
    border-top: 1px solid #18181b;
    border-bottom: 1px solid #18181b;
    margin: 0;
    padding: 2.5rem 4rem;
    background: #09090b;
}
.stat-item {
    flex: 1;
    text-align: center;
    padding: 0 2rem;
    border-right: 1px solid #18181b;
}
.stat-item:last-child { border-right: none; }
.stat-value { font-size: 2.5rem; font-weight: 800; color: #fafafa; letter-spacing: -0.04em; }
.stat-label { font-size: 0.8rem; color: #52525b; margin-top: 0.25rem; text-transform: uppercase; letter-spacing: 0.06em; }

/* ── SECTION ─────────────────────────── */
.section { padding: 6rem 4rem; max-width: 1200px; margin: 0 auto; }
.section-label {
    font-size: 0.75rem; color: #22d3ee; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase;
    margin-bottom: 1rem;
}
.section-title {
    font-size: clamp(1.75rem, 3vw, 2.5rem);
    font-weight: 700; color: #fafafa;
    letter-spacing: -0.03em; line-height: 1.2;
    margin: 0 0 1rem;
}
.section-sub { font-size: 1.05rem; color: #71717a; max-width: 480px; line-height: 1.7; }

/* ── FEATURE GRID ────────────────────── */
.feat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: #18181b;
    border: 1px solid #18181b;
    border-radius: 12px;
    overflow: hidden;
    margin-top: 4rem;
}
.feat-cell {
    background: #09090b;
    padding: 2rem;
    transition: background 0.15s;
}
.feat-cell:hover { background: #0f0f12; }
.feat-icon {
    width: 40px; height: 40px;
    background: #18181b; border: 1px solid #27272a;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; margin-bottom: 1.25rem;
}
.feat-title { font-size: 0.95rem; font-weight: 600; color: #fafafa; margin-bottom: 0.5rem; }
.feat-desc  { font-size: 0.875rem; color: #71717a; line-height: 1.6; }

/* ── FIELDS TABLE ────────────────────── */
.fields-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: #18181b;
    border: 1px solid #18181b;
    border-radius: 12px;
    overflow: hidden;
    margin-top: 3rem;
}
.fields-col { background: #09090b; padding: 1.5rem; }
.fields-col-title { font-size: 0.75rem; font-weight: 600; color: #52525b; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 1rem; }
.field-item {
    display: flex; align-items: center; gap: 0.5rem;
    font-size: 0.85rem; color: #a1a1aa;
    padding: 0.35rem 0;
    border-bottom: 1px solid #18181b;
}
.field-item:last-child { border-bottom: none; }
.field-dot { width: 6px; height: 6px; border-radius: 50%; background: #22d3ee; flex-shrink: 0; }

/* ── PRICING ─────────────────────────── */
.pricing-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-top: 3rem;
}
.price-card {
    background: #0f0f12;
    border: 1px solid #1f1f23;
    border-radius: 12px;
    padding: 1.75rem;
    position: relative;
    transition: border-color 0.15s;
}
.price-card:hover { border-color: #3f3f46; }
.price-card.featured {
    border-color: #22d3ee;
    background: #0c1a1f;
}
.price-badge {
    position: absolute; top: -12px; left: 50%; transform: translateX(-50%);
    background: #22d3ee; color: #09090b;
    padding: 2px 14px; border-radius: 100px;
    font-size: 0.75rem; font-weight: 700;
    white-space: nowrap;
}
.price-name  { font-size: 0.875rem; font-weight: 600; color: #a1a1aa; margin-bottom: 0.75rem; }
.price-amount { font-size: 2.25rem; font-weight: 800; color: #fafafa; letter-spacing: -0.04em; line-height: 1; }
.price-period { font-size: 0.8rem; color: #52525b; margin-top: 0.25rem; margin-bottom: 1.25rem; }
.price-divider { border: none; border-top: 1px solid #1f1f23; margin: 1.25rem 0; }
.price-feature { font-size: 0.8rem; color: #71717a; padding: 0.3rem 0; display: flex; align-items: center; gap: 0.5rem; }
.price-feature::before { content: "✓"; color: #22d3ee; font-weight: 700; font-size: 0.75rem; }
.price-btn {
    display: block; width: 100%;
    padding: 0.6rem;
    border-radius: 6px;
    font-size: 0.85rem; font-weight: 600;
    text-align: center;
    cursor: pointer;
    margin-top: 1.25rem;
    border: 1px solid #27272a;
    background: transparent;
    color: #fafafa;
    transition: all 0.15s;
    text-decoration: none;
}
.price-card.featured .price-btn {
    background: #22d3ee; color: #09090b; border-color: transparent;
}

/* ── TESTIMONIALS ────────────────────── */
.testi-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 3rem; }
.testi-card {
    background: #0f0f12;
    border: 1px solid #1f1f23;
    border-radius: 12px;
    padding: 1.75rem;
}
.testi-quote { font-size: 0.9rem; color: #a1a1aa; line-height: 1.75; margin-bottom: 1.25rem; }
.testi-author { font-size: 0.85rem; font-weight: 600; color: #fafafa; }
.testi-role   { font-size: 0.8rem; color: #52525b; }
.testi-stars  { color: #eab308; font-size: 0.8rem; margin-bottom: 0.75rem; }

/* ── CTA BLOCK ───────────────────────── */
.cta-block {
    border: 1px solid #1f1f23;
    border-radius: 16px;
    padding: 4rem;
    text-align: center;
    background: linear-gradient(135deg, #0f1a1f 0%, #0f0f12 100%);
    margin: 0 4rem 6rem;
}
.cta-title { font-size: 2.25rem; font-weight: 700; color: #fafafa; letter-spacing: -0.03em; margin: 0 0 1rem; }
.cta-sub   { font-size: 1rem; color: #71717a; margin: 0 0 2rem; }

/* ── FOOTER ──────────────────────────── */
.footer {
    border-top: 1px solid #18181b;
    padding: 2rem 4rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #52525b;
    font-size: 0.8rem;
}
</style>
""", unsafe_allow_html=True)

# NAV
st.markdown("""
<nav class="nav">
    <div class="nav-logo">🚢 DocExtract Pro</div>
    <div class="nav-links">
        <a href="#">Produkt</a>
        <a href="#">Preise</a>
        <a href="#">Dokumentation</a>
        <a href="#">API</a>
    </div>
    <button class="nav-cta">Kostenlos testen</button>
</nav>
""", unsafe_allow_html=True)

# HERO
st.markdown("""
<div style="padding: 7rem 4rem 5rem; text-align: center; max-width: 900px; margin: 0 auto;">
    <div class="hero-badge">
        <span>Neu</span> · Jetzt mit Batch-Verarbeitung und Webhook-Support
    </div>
    <h1 class="hero-h1">
        Logistikdokumente<br>
        <em>automatisch auslesen</em>
    </h1>
    <p class="hero-sub">
        DocExtract Pro extrahiert alle Daten aus Sea Waybills, Bills of Lading und Rechnungen —
        in Sekunden, mit KI-Präzision, direkt in dein System.
    </p>
    <div class="hero-actions">
        <a href="/" class="btn-primary">Demo starten →</a>
        <a href="#" class="btn-secondary">API Docs ansehen</a>
    </div>
</div>
""", unsafe_allow_html=True)

# STATS
st.markdown("""
<div class="stats-bar">
    <div class="stat-item">
        <div class="stat-value">&lt;10s</div>
        <div class="stat-label">Extraktionszeit</div>
    </div>
    <div class="stat-item">
        <div class="stat-value">15+</div>
        <div class="stat-label">Felder pro Dokument</div>
    </div>
    <div class="stat-item">
        <div class="stat-value">98%</div>
        <div class="stat-label">Genauigkeit</div>
    </div>
    <div class="stat-item">
        <div class="stat-value">€0.49</div>
        <div class="stat-label">Pro Dokument</div>
    </div>
    <div class="stat-item">
        <div class="stat-value">∞</div>
        <div class="stat-label">Batch-Größe</div>
    </div>
</div>
""", unsafe_allow_html=True)

# FEATURES
st.markdown("""
<div class="section">
    <div class="section-label">Funktionen</div>
    <div class="section-title">Alles was Enterprise braucht</div>
    <div class="section-sub">Von der Extraktion bis zur Integration — vollständig abgedeckt.</div>
    <div class="feat-grid">
        <div class="feat-cell">
            <div class="feat-icon">🤖</div>
            <div class="feat-title">KI-Extraktion</div>
            <div class="feat-desc">Claude AI liest jedes Dokument mit Zero-Hallucination-Garantie via Pydantic-Validierung.</div>
        </div>
        <div class="feat-cell">
            <div class="feat-icon">🔄</div>
            <div class="feat-title">Batch-Verarbeitung</div>
            <div class="feat-desc">Hunderte PDFs gleichzeitig. Parallel verarbeitet, komplett exportiert.</div>
        </div>
        <div class="feat-cell">
            <div class="feat-icon">🔑</div>
            <div class="feat-title">REST API</div>
            <div class="feat-desc">Direkte Integration in SAP, TMS und eigene Systeme via API Key.</div>
        </div>
        <div class="feat-cell">
            <div class="feat-icon">🔔</div>
            <div class="feat-title">Webhooks</div>
            <div class="feat-desc">Ergebnisse automatisch in dein System pushen, sobald fertig.</div>
        </div>
        <div class="feat-cell">
            <div class="feat-icon">📊</div>
            <div class="feat-title">Audit-Dashboard</div>
            <div class="feat-desc">Vollständige History, Kosten, Erfolgsraten und CSV-Export.</div>
        </div>
        <div class="feat-cell">
            <div class="feat-icon">🛡️</div>
            <div class="feat-title">DSGVO-konform</div>
            <div class="feat-desc">EU-Hosting. Keine Dokumentenspeicherung. Row-Level Security.</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# FIELDS
st.markdown("""
<div class="section" style="padding-top: 0;">
    <div class="section-label">Datenfelder</div>
    <div class="section-title">15+ Felder pro Dokument</div>
    <div class="fields-grid">
        <div class="fields-col">
            <div class="fields-col-title">Dokument</div>
            <div class="field-item"><div class="field-dot"></div>Dokumenttyp</div>
            <div class="field-item"><div class="field-dot"></div>Dokumentnummer</div>
            <div class="field-item"><div class="field-dot"></div>Ausstellungsdatum</div>
            <div class="field-item"><div class="field-dot"></div>Buchungsnummer</div>
            <div class="field-item"><div class="field-dot"></div>Purchase Order</div>
        </div>
        <div class="fields-col">
            <div class="fields-col-title">Parteien</div>
            <div class="field-item"><div class="field-dot"></div>Absender + Adresse</div>
            <div class="field-item"><div class="field-dot"></div>Empfänger + Adresse</div>
            <div class="field-item"><div class="field-dot"></div>Notify Party</div>
            <div class="field-item"><div class="field-dot"></div>Spediteur</div>
            <div class="field-item"><div class="field-dot"></div>Frachtführer</div>
        </div>
        <div class="fields-col">
            <div class="fields-col-title">Transport</div>
            <div class="field-item"><div class="field-dot"></div>Schiff + IMO</div>
            <div class="field-item"><div class="field-dot"></div>Voyage-Nummer</div>
            <div class="field-item"><div class="field-dot"></div>Verladehafen</div>
            <div class="field-item"><div class="field-dot"></div>Löschhafen</div>
            <div class="field-item"><div class="field-dot"></div>ETD / ETA</div>
        </div>
        <div class="fields-col">
            <div class="fields-col-title">Ladung</div>
            <div class="field-item"><div class="field-dot"></div>Container-Nummern</div>
            <div class="field-item"><div class="field-dot"></div>Container-Typen</div>
            <div class="field-item"><div class="field-dot"></div>Gewicht + CBM</div>
            <div class="field-item"><div class="field-dot"></div>HS-Codes</div>
            <div class="field-item"><div class="field-dot"></div>Incoterms</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# PRICING
st.markdown("""
<div class="section" style="padding-top: 0;">
    <div class="section-label">Preise</div>
    <div class="section-title">Pay-as-you-go</div>
    <div class="section-sub">Keine Monatsgebühren. Keine Mindestlaufzeit.</div>
    <div class="pricing-grid">
        <div class="price-card">
            <div class="price-name">Starter</div>
            <div class="price-amount">€4.90</div>
            <div class="price-period">10 Credits · €0.49/Doc</div>
            <hr class="price-divider">
            <div class="price-feature">10 Dokumente</div>
            <div class="price-feature">CSV + JSON Export</div>
            <div class="price-feature">Dashboard</div>
            <a href="#" class="price-btn">Kaufen</a>
        </div>
        <div class="price-card featured">
            <div class="price-badge">Beliebt</div>
            <div class="price-name">Business</div>
            <div class="price-amount">€19.90</div>
            <div class="price-period">50 Credits · €0.40/Doc</div>
            <hr class="price-divider">
            <div class="price-feature">50 Dokumente</div>
            <div class="price-feature">CSV + JSON + Excel</div>
            <div class="price-feature">API Keys</div>
            <div class="price-feature">Webhooks</div>
            <a href="#" class="price-btn">Kaufen</a>
        </div>
        <div class="price-card">
            <div class="price-name">Pro</div>
            <div class="price-amount">€69.90</div>
            <div class="price-period">200 Credits · €0.35/Doc</div>
            <hr class="price-divider">
            <div class="price-feature">200 Dokumente</div>
            <div class="price-feature">Batch-Verarbeitung</div>
            <div class="price-feature">Email-Benachrichtigungen</div>
            <div class="price-feature">Priority Support</div>
            <a href="#" class="price-btn">Kaufen</a>
        </div>
        <div class="price-card">
            <div class="price-name">Enterprise</div>
            <div class="price-amount">Custom</div>
            <div class="price-period">Ab 1.000 Docs/Monat</div>
            <hr class="price-divider">
            <div class="price-feature">Unbegrenzte Dokumente</div>
            <div class="price-feature">SLA-Garantie</div>
            <div class="price-feature">Dedicated Support</div>
            <div class="price-feature">On-Premise Option</div>
            <a href="#" class="price-btn">Anfragen</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# TESTIMONIALS
st.markdown("""
<div class="section" style="padding-top: 0;">
    <div class="section-label">Referenzen</div>
    <div class="section-title">Vertraut von Spediteuren</div>
    <div class="testi-grid">
        <div class="testi-card">
            <div class="testi-stars">★★★★★</div>
            <div class="testi-quote">"Wir verarbeiten täglich 300+ Sea Waybills. Mit DocExtract sparen wir 2 Stunden Abtippen pro Tag."</div>
            <div class="testi-author">Thomas K.</div>
            <div class="testi-role">Operations Manager · Hamburg</div>
        </div>
        <div class="testi-card">
            <div class="testi-stars">★★★★★</div>
            <div class="testi-quote">"API-Integration in unser TMS in einem Nachmittag erledigt. Dokumentation ist exzellent."</div>
            <div class="testi-author">Maria L.</div>
            <div class="testi-role">IT-Leiterin · Bremen</div>
        </div>
        <div class="testi-card">
            <div class="testi-stars">★★★★★</div>
            <div class="testi-quote">"Keine Tippfehler mehr. Das Tool zahlt sich in der ersten Woche aus."</div>
            <div class="testi-author">Andreas M.</div>
            <div class="testi-role">Geschäftsführer · Frankfurt</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# CTA
st.markdown("""
<div class="cta-block">
    <div class="cta-title">Bereit loszulegen?</div>
    <div class="cta-sub">3 kostenlose Extraktionen — keine Kreditkarte nötig.</div>
    <div style="display:flex;gap:1rem;justify-content:center;">
        <a href="/" class="btn-primary">Demo starten →</a>
        <a href="#" class="btn-secondary">Sales kontaktieren</a>
    </div>
</div>
""", unsafe_allow_html=True)

# FOOTER
st.markdown("""
<div class="footer">
    <div>© 2026 DocExtract Pro · Alle Rechte vorbehalten</div>
    <div style="display:flex;gap:2rem;">
        <a href="#" style="color:#52525b;text-decoration:none;">Datenschutz</a>
        <a href="#" style="color:#52525b;text-decoration:none;">Impressum</a>
        <a href="#" style="color:#52525b;text-decoration:none;">support@docextract.pro</a>
    </div>
</div>
""", unsafe_allow_html=True)
