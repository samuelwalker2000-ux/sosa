@echo off
:: send_daily_report.bat
:: Pulls the latest market report from GitHub and emails it.
:: Run by Windows Task Scheduler at 7:30 AM daily.

set WORKSPACE=C:\Users\User\OneDrive\Documents\Sam's Documents\Claude\claude

:: Pull latest report from GitHub
cd /d "%WORKSPACE%"
git pull origin main >> "%WORKSPACE%\scripts\send_log.txt" 2>&1

:: Send the email
python "%WORKSPACE%\scripts\send_market_report.py" >> "%WORKSPACE%\scripts\send_log.txt" 2>&1
