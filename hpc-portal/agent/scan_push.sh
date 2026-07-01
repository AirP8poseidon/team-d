#!/usr/bin/env bash
# 방식 A — git 경유 전송 (맥↔클러스터 망 격리, git만 연결될 때).
# master(또는 클러스터의 git 가능한 호스트)에서 실행:
#   node1..node13 을 SSH 순회 → collect_node.py(python2.7)로 수집
#   → hpc-portal/data/live/<node>.json 에 모아 git commit + push.
# 맥(포털)은 git pull 후 COLLECTOR=ingest 로 data/live 를 읽어 표시.
#
# 사용(master에서):
#   bash hpc-portal/agent/scan_push.sh            # 1회
#   bash hpc-portal/agent/scan_push.sh --loop     # INTERVAL(기본 30s)마다
#
# 전제:
#   - master → 각 node SSH 무암호(HPC 표준). 공유 FS면 collect_node.py 한 경로로 충분.
#   - 노드 파이썬은 python(2.7). 다르면 NODE_PYTHON 으로 지정.
#   - 이 호스트에서 git push 가능(정찰 때 확인됨).
set -u

_HERE="$(cd "$(dirname "$0")" && pwd)"
_REPO="$(cd "$_HERE/../.." && pwd)"                       # team-d repo 루트
NODES="${HPC_NODES:-master node1 node2 node3 node4 node5 node6 node7 node8 node9 node10 node11 node12 node13}"
NODES="${NODES//,/ }"
LIVE="$_REPO/hpc-portal/data/live"
COLLECTOR="${COLLECTOR_PATH:-$_HERE/collect_node.py}"     # 각 노드에서 실행(공유 FS 경로)
PY="${NODE_PYTHON:-python}"                               # 노드 파이썬(기본 python=2.7)
SSH_USER="${SSH_USER:-}"
INTERVAL="${INTERVAL:-30}"                                # git 왕복이라 30초 권장
SELF="$(hostname -s 2>/dev/null || hostname)"
mkdir -p "$LIVE"

_collect() {  # $1=node → JSON(stdout)
  local n="$1"
  if [ "$n" = "$SELF" ] || [ "$n" = "localhost" ]; then
    "$PY" "$COLLECTOR" "$n" 2>/dev/null
  else
    local t="$n"; [ -n "$SSH_USER" ] && t="$SSH_USER@$n"
    ssh -o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new \
        "$t" "$PY '$COLLECTOR' '$n'" 2>/dev/null
  fi
}

scan_and_push() {
  local wrote=0
  for n in $NODES; do
    local j; j="$(_collect "$n")"
    if [ -n "$j" ]; then printf '%s' "$j" > "$LIVE/$n.json"; echo "  $n ✓"; wrote=1
    else echo "  $n ✗ (ssh/python/collect_node 확인)" >&2; fi
  done
  [ "$wrote" = 1 ] || { echo "  수집 0 — push 생략"; return 0; }
  ( cd "$_REPO" || exit 0
    git add hpc-portal/data/live/*.json 2>/dev/null
    git diff --cached --quiet && { echo "  변동 없음 — commit 생략"; exit 0; }
    git -c user.name="cluster-scan" -c user.email="scan@hpc.local" \
        commit -q -m "live: $(date +%Y-%m-%dT%H:%M:%S) 노드 상태"
    if git pull --rebase -q origin main && git push -q origin main; then
      echo "  → git push 완료"
    else
      echo "  → git push 실패(네트워크/충돌 확인)" >&2
    fi )
}

if [ "${1:-}" = "--loop" ]; then
  echo "git-경유 스캔 ${INTERVAL}s 간격 → $LIVE (Ctrl+C 종료)"
  while true; do echo "[$(date +%H:%M:%S)] scan"; scan_and_push; sleep "$INTERVAL"; done
else
  scan_and_push
fi
