@echo off
REM 저빈도 라이브 갱신 — 이 창을 열어두면 180초마다 master 스캔 + 수집(포털에 반영).
REM 닫으려면 이 창에서 Ctrl+C 또는 창 닫기.
cd /d "%~dp0"
echo ================================================================
echo  HPC Portal  -  live refresh (180s)   대상: Geo83-gonas
echo  종료: Ctrl+C
echo ================================================================
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0refresh_loop.ps1" -IntervalSec 180
pause
