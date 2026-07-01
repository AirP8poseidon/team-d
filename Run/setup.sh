#!/usr/bin/env bash
# ── 최초 1회: 가상환경(.venv) + 의존성 설치 (mac/linux) ──
set -e
cd "$(dirname "$0")/../hpc-portal"
echo "================================================================"
echo " HPC Portal  setup  (venv + pip install)"
echo "================================================================"
if ! command -v python3 >/dev/null 2>&1; then
  echo "[!] python3 를 찾을 수 없습니다. Python 3.10+ 설치 후 다시 실행하세요."
  exit 1
fi
[ -x ".venv/bin/python" ] || { echo "[*] 가상환경 생성..."; python3 -m venv .venv; }
echo "[*] 의존성 설치..."
.venv/bin/python -m pip install -r requirements.txt
echo
echo "[완료] 이제 ./start_server.sh 로 실행하세요."
