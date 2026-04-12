@echo off
:: run_market_report.bat
:: Runs Claude locally to generate the daily market report and email it.
:: Triggered by Windows Task Scheduler at 7:00 AM daily.

set WORKSPACE=C:\Users\User\OneDrive\Documents\Sam's Documents\Claude\claude
set LOG=%WORKSPACE%\scripts\local_run_log.txt

echo. >> "%LOG%"
echo [%date% %time%] ===== Starting market report ===== >> "%LOG%"

cd /d "%WORKSPACE%"

claude -p "Read .claude/commands/market-report.md and follow all its instructions exactly to generate today's market report, save it, and email it to samuelwalker2000@gmail.com." --permission-mode auto --allowedTools "WebSearch,WebFetch,Bash,Read,Write,Edit,Glob,Grep" >> "%LOG%" 2>&1

echo [%date% %time%] ===== Done ===== >> "%LOG%"
