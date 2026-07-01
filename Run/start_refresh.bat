@echo off
REM ── 라이브 갱신 루프 (ingest 모드일 때) ──
REM   180초마다 master 에서 전 노드 스캔 + scp 수집 → 포털에 반영(읽기전용·저빈도).
setlocal
cd /d "%~dp0..\hpc-portal"
echo ================================================================
echo  HPC Portal  live refresh  (180초 주기, 대상: Geo83-gonas)
echo  종료 : 이 창에서 Ctrl+C
echo ================================================================
powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\refresh_loop.ps1" -IntervalSec 180
pause
