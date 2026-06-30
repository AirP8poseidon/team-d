@echo off
REM HPC 포털 데모 서버 (외부 LAN 공개) — 이 창을 열어두면 서버가 계속 떠 있습니다.
REM 닫으려면 이 창에서 Ctrl+C 또는 창 닫기.
cd /d "%~dp0"
set COLLECTOR=ingest
set HPC_NODES=master,node1,node2,node3,node4,node5,node6,node7,node8,node9,node10,node11,node12,node13
set HPC_DB_PATH=%~dp0demo.db
echo ================================================================
echo  HPC Portal  -  http://10.27.1.103:8000   (LAN)
echo  COLLECTOR=%COLLECTOR%   NODES=master,node1..node13
echo  종료: Ctrl+C
echo ================================================================
".venv\Scripts\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8000
pause
