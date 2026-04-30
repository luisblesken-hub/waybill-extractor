@echo off
cd /d "%~dp0"
git add .
git commit -m "feat: enterprise v2 - landing, webhooks, excel, schemas"
git push
pause
