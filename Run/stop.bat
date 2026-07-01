@echo off
REM ── 서버 + 라이브 갱신 루프 종료 ──
echo === HPC Portal 종료 ===
echo [*] 포트 8000 서버 종료...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8000" ^| findstr LISTENING') do (
  taskkill /PID %%p /F >nul 2>&1 && echo     - PID %%p 종료
)
echo [*] refresh 루프 종료...
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='powershell.exe'\" | Where-Object { $_.CommandLine -like '*-File*refresh_loop*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }" >nul 2>&1
echo [완료]
pause
