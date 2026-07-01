@echo off
REM ── 서버 실행 (mock = 샘플 데이터) — 클러스터 없이 어디서나 동작 (채점·체험용) ──
setlocal
cd /d "%~dp0..\hpc-portal"
if not exist ".venv\Scripts\python.exe" (
  echo [!] .venv 없음 — 먼저 setup.bat 을 실행하세요.
  pause & exit /b 1
)
set COLLECTOR=mock
set HPC_DB_PATH=%CD%\demo.db
echo ================================================================
echo  HPC Portal  (mock = 샘플 데이터, node01~08)
echo  로컬 : http://localhost:8000     ( API 문서: /docs )
echo  종료 : 이 창에서 Ctrl+C  또는  stop.bat
echo ================================================================
".venv\Scripts\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8000
pause
