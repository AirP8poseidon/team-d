#!/usr/bin/env bash
# 클러스터 스캐너 — 한 호스트(master 또는 워크스테이션)에서 모든 노드를 SSH로 순회하며
# 각 노드의 자원 정보를 수집해 포털의 data/incoming/<node>.json 으로 모은다.
# (노드마다 에이전트를 띄우는 push 대신, 한 곳에서 loop-scan 하는 pull 방식.)
#
# 전제:
#   - 이 스크립트를 돌리는 호스트가 각 노드로 SSH 가능(HPC면 보통 master→nodes 무암호 키 있음).
#   - 각 노드에서 node_report.py 를 python3 로 실행 가능(공유 FS면 한 경로로 충분,
#     아니면 노드마다 1회 scp). 자기 자신/master 는 로컬 실행.
#
# 노드 목록(기본: master + node1..node13). 환경변수로 변경:
#   HPC_NODES="master,node1,node2,...,node13"   (콤마 또는 공백 구분)
#
# 사용:
#   bash scan_cluster.sh             # 1회 스캔
#   bash scan_cluster.sh --loop      # INTERVAL 초마다 반복
#
# 포털이 다른 호스트면(이 스캐너는 master, 포털은 워크스테이션) PORTAL_HOST 설정 →
# 로컬 incoming 대신 scp 로 포털에 푸시:
#   PORTAL_HOST=10.10.9.101 PORTAL_USER=mac-leesh \
#   PORTAL_INCOMING=Develop/Projects/GEOSR_hackton/team-d/hpc-portal/data/incoming \
#   bash scan_cluster.sh --loop
set -u

_HERE="$(cd "$(dirname "$0")" && pwd)"
NODES="${HPC_NODES:-master node1 node2 node3 node4 node5 node6 node7 node8 node9 node10 node11 node12 node13}"
NODES="${NODES//,/ }"                       # 콤마도 공백으로
AGENT="${AGENT:-$_HERE/node_report.py}"     # 각 노드에서 실행할 에이전트 경로(공유 FS 가정)
SSH_USER="${SSH_USER:-}"                    # 노드 SSH 계정(비우면 현재 사용자)
INTERVAL="${INTERVAL:-5}"
SELF="$(hostname -s 2>/dev/null || hostname)"

# 수집물 목적지: PORTAL_HOST 설정 시 scp, 아니면 로컬 incoming
LOCAL_INCOMING="${INCOMING:-$(cd "$_HERE/../data/incoming" 2>/dev/null && pwd)}"
PORTAL_HOST="${PORTAL_HOST:-}"
PORTAL_USER="${PORTAL_USER:-}"
PORTAL_INCOMING="${PORTAL_INCOMING:-$LOCAL_INCOMING}"

_get_json() {  # $1=node → 그 노드의 JSON 을 stdout 으로
  local n="$1"
  if [ "$n" = "$SELF" ] || [ "$n" = "localhost" ]; then
    python3 "$AGENT" --node "$n" --stdout 2>/dev/null
  else
    local tgt="$n"; [ -n "$SSH_USER" ] && tgt="$SSH_USER@$n"
    ssh -o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new \
        "$tgt" "python3 '$AGENT' --node '$n' --stdout" 2>/dev/null
  fi
}

_deliver() {  # $1=node $2=json
  local n="$1" json="$2"
  if [ -n "$PORTAL_HOST" ]; then
    local tmp="/tmp/$n.json"; printf '%s' "$json" > "$tmp"
    local tgt="$PORTAL_HOST"; [ -n "$PORTAL_USER" ] && tgt="$PORTAL_USER@$PORTAL_HOST"
    scp -q -o StrictHostKeyChecking=accept-new "$tmp" "$tgt:$PORTAL_INCOMING/$n.json"
  else
    printf '%s' "$json" > "$LOCAL_INCOMING/$n.json"
  fi
}

scan_once() {
  local ok=0 fail=0
  echo "[$(date +%H:%M:%S)] scan: $NODES"
  for n in $NODES; do
    local json; json="$(_get_json "$n")"
    if [ -n "$json" ]; then
      if _deliver "$n" "$json"; then echo "  $n ✓"; ok=$((ok+1)); else echo "  $n ✗ (전송 실패)" >&2; fail=$((fail+1)); fi
    else
      echo "  $n ✗ (ssh/python3/에이전트 확인)" >&2; fail=$((fail+1))
    fi
  done
  echo "  → 성공 $ok / 실패 $fail"
}

if [ "${1:-}" = "--loop" ]; then
  dest="${PORTAL_HOST:+$PORTAL_USER@$PORTAL_HOST:}$PORTAL_INCOMING"
  echo "loop-scan ${INTERVAL}s 간격 → $dest  (Ctrl+C 종료)"
  while true; do scan_once; sleep "$INTERVAL"; done
else
  scan_once
fi
