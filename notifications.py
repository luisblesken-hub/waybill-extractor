"""
DocExtract Pro — Email notifications via Resend
"""
import os
from typing import Optional

def send_extraction_complete(
    to_email: str,
    filename: str,
    doc_type: str,
    doc_number: Optional[str],
    success: bool,
    latency_s: float,
    fields_count: int
):
    """Send extraction completion email via Resend."""
    api_key = os.environ.get("RESEND_API_KEY", "")
    if not api_key:
        return  # Silent fail if no key configured

    try:
        import resend
        resend.api_key = api_key

        status_icon = "✅" if success else "❌"
        status_text = "Erfolgreich extrahiert" if success else "Extraktion fehlgeschlagen"

        html = f"""
        <div style="font-family:Inter,sans-serif;max-width:600px;margin:0 auto;">
            <div style="background:linear-gradient(135deg,#0f2027,#2c5364);padding:2rem;border-radius:12px 12px 0 0;color:white;">
                <h1 style="margin:0;font-size:1.5rem;">🚢 DocExtract Pro</h1>
                <p style="margin:0.5rem 0 0;opacity:0.8;">Extraktionsbericht</p>
            </div>
            <div style="background:white;border:1px solid #e5e7eb;border-top:none;padding:2rem;border-radius:0 0 12px 12px;">
                <h2 style="color:#111827;">{status_icon} {status_text}</h2>
                <table style="width:100%;border-collapse:collapse;">
                    <tr><td style="padding:8px 0;color:#6b7280;">Datei:</td><td style="font-weight:600;">{filename}</td></tr>
                    <tr><td style="padding:8px 0;color:#6b7280;">Dokumenttyp:</td><td>{doc_type}</td></tr>
                    <tr><td style="padding:8px 0;color:#6b7280;">Dokumentnummer:</td><td>{doc_number or '—'}</td></tr>
                    <tr><td style="padding:8px 0;color:#6b7280;">Felder extrahiert:</td><td>{fields_count}</td></tr>
                    <tr><td style="padding:8px 0;color:#6b7280;">Verarbeitungszeit:</td><td>{latency_s}s</td></tr>
                    <tr><td style="padding:8px 0;color:#6b7280;">Kosten:</td><td>€0.49</td></tr>
                </table>
                <div style="margin-top:1.5rem;padding:1rem;background:#f9fafb;border-radius:8px;font-size:0.85rem;color:#6b7280;">
                    Dokument wurde sicher verarbeitet und nicht gespeichert.
                </div>
            </div>
        </div>
        """

        resend.Emails.send({
            "from":    "DocExtract Pro <notifications@docextract.pro>",
            "to":      [to_email],
            "subject": f"{status_icon} Extraktion abgeschlossen: {filename}",
            "html":    html,
        })
    except Exception:
        pass  # Never block main flow for email failures


def send_welcome_email(to_email: str):
    """Send welcome email to new users."""
    api_key = os.environ.get("RESEND_API_KEY", "")
    if not api_key:
        return

    try:
        import resend
        resend.api_key = api_key

        html = """
        <div style="font-family:Inter,sans-serif;max-width:600px;margin:0 auto;">
            <div style="background:linear-gradient(135deg,#0f2027,#2c5364);padding:2rem;border-radius:12px 12px 0 0;color:white;">
                <h1 style="margin:0;font-size:1.5rem;">🚢 Willkommen bei DocExtract Pro</h1>
            </div>
            <div style="background:white;border:1px solid #e5e7eb;border-top:none;padding:2rem;border-radius:0 0 12px 12px;">
                <p>Schön, dass du dabei bist!</p>
                <p>Dein Konto ist aktiviert. Du hast <strong>3 kostenlose Extraktionen</strong> zum Testen.</p>
                <h3>So startest du:</h3>
                <ol>
                    <li>Öffne die App und melde dich an</li>
                    <li>Lade ein Sea Waybill oder Bill of Lading als PDF hoch</li>
                    <li>Lade die extrahierten Daten als CSV oder JSON herunter</li>
                </ol>
                <p style="color:#6b7280;font-size:0.85rem;">Fragen? Antworte auf diese E-Mail.</p>
            </div>
        </div>
        """

        resend.Emails.send({
            "from":    "DocExtract Pro <hello@docextract.pro>",
            "to":      [to_email],
            "subject": "Willkommen bei DocExtract Pro 🚢",
            "html":    html,
        })
    except Exception:
        pass


def send_low_credits_alert(to_email: str, remaining: int):
    """Alert user when credits are running low."""
    api_key = os.environ.get("RESEND_API_KEY", "")
    if not api_key:
        return

    try:
        import resend
        resend.api_key = api_key

        resend.Emails.send({
            "from":    "DocExtract Pro <notifications@docextract.pro>",
            "to":      [to_email],
            "subject": f"⚠️ Nur noch {remaining} Credits verfügbar",
            "html":    f"<p>Du hast nur noch <strong>{remaining} Credits</strong>. Jetzt aufladen!</p>",
        })
    except Exception:
        pass
