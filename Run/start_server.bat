@echo off
REM ── 서버 실행 (ingest = 실 클러스터 데이터) — 데모 PC 전용 ──
REM   data/incoming/*.json (master 스캔 결과)를 읽어 표시. 라이브 갱신은 start_refresh.bat.
setlocal
cd /d "%~dp0..\hpc-portal"
if not exist ".venv\Scripts\python.exe" (
  echo [!] .venv 없음 — 먼저 setup.bat 을 실행하세요.
  pause & exit /b 1
)
set COLLECTOR=ingest
set HPC_NODES=master,node1,node2,node3,node4,node5,node6,node7,node8,node9,node10,node11,node12,node13
set HPC_DB_PATH=%CD%\demo.db
echo ================================================================
echo  HPC Portal  (ingest = 실 클러스터)
echo  로컬 : http://localhost:8000
echo  LAN  : http://^<이 PC IP^>:8000   (ipconfig 로 IP 확인)
echo  종료 : 이 창에서 Ctrl+C  또는  stop.bat
echo ================================================================
".venv\Scripts\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8000
pause
