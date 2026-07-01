@echo off
REM ── 최초 1회: 가상환경(.venv) + 의존성 설치 ──
setlocal
cd /d "%~dp0..\hpc-portal"
echo ================================================================
echo  HPC Portal  setup  (venv + pip install)
echo ================================================================
where python >nul 2>&1
if errorlevel 1 (
  echo [!] python 을 찾을 수 없습니다. Python 3.10+ 설치 후 다시 실행하세요.
  pause & exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo [*] 가상환경 생성...
  python -m venv .venv
)
echo [*] 의존성 설치...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
echo.
echo [완료] 이제 start_server_mock.bat (또는 start_server.bat) 로 실행하세요.
pause
