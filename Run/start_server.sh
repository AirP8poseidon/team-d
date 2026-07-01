#!/usr/bin/env bash
# ── 서버 실행 (mac/linux) ──
#   기본 mock(샘플). 실데이터는:  COLLECTOR=ingest ./start_server.sh
set -e
cd "$(dirname "$0")/../hpc-portal"

if [ ! -x ".venv/bin/python" ]; then
  echo "[!] .venv 없음 — 먼저 ./setup.sh 를 실행하세요."
  exit 1
fi

export COLLECTOR="${COLLECTOR:-mock}"
if [ "$COLLECTOR" = "ingest" ]; then
  export HPC_NODES="${HPC_NODES:-master,node1,node2,node3,node4,node5,node6,node7,node8,node9,node10,node11,node12,node13}"
fi
export HPC_DB_PATH="$PWD/demo.db"

echo "================================================================"
echo " HPC Portal  (COLLECTOR=$COLLECTOR)"
echo " 로컬 : http://localhost:8000     (API 문서: /docs)"
echo " LAN  : http://<이 PC IP>:8000"
echo " 종료 : Ctrl+C"
echo "================================================================"
exec .venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
