# Setup-Script für Waybill Extractor
Write-Host "Setup wird gestartet..." -ForegroundColor Green

py -m venv venv
.\venv\Scripts\activate
py -m pip install --upgrade pip
pip install -r requirements.txt

if (!(Test-Path ".env")) {
    Copy-Item ".env.template" ".env"
    Write-Host "WICHTIG: .env Datei erstellt. API Key eintragen!" -ForegroundColor Yellow
}

Write-Host "Setup abgeschlossen! Starten mit: streamlit run app.py" -ForegroundColor Green
