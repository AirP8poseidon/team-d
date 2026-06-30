#!/usr/bin/env bash
# 1회성 클러스터 스캔 — 이 클러스터 전용(RHEL7 / python2.7 / GPU 없음 / 직접 SSH 가능).
# master 에서 실행: master + node1..node13 을 "순차" SSH 순회하며 collect_node.py(py2.7)로
# 자원/실행작업을 수집해 hpc-portal/data/incoming/<node>.json 에 쓴다.
# 사무실 PC(포털)는 이 incoming/*.json 을 scp 로 받아 COLLECTOR=ingest 로 표시한다.
#
# 부하 최소 원칙(서버 보호):
#   - 병렬 fan-out 금지(순차) · --loop 없음(1회성) · ConnectTimeout 짧게 · 읽기 전용 수집만.
#   - 주기 갱신이 필요하면 이 스크립트를 cron/watch 로 "바깥에서" 낮은 빈도로 부른다.
#
# 사용(master 에서):
#   bash hpc-portal/agent/scan_once.sh
#   HPC_NODES="master,node1,node2" bash hpc-portal/agent/scan_once.sh   # 일부만
#
# 환경변수:
#   HPC_NODES   노드 목록(콤마/공백). 기본 master node1..node13
#   NODE_PYTHON 노드 파이썬(기본 python = 2.7)
#   SSH_USER    노드 SSH 계정(기본: 현재 사용자)
#   TIMEOUT     SSH ConnectTimeout 초(기본 6)
set -u

_HERE="$(cd "$(dirname "$0")" && pwd)"
NODES="${HPC_NODES:-master node1 node2 node3 node4 node5 node6 node7 node8 node9 node10 node11 node12 node13}"
NODES="${NODES//,/ }"
COLLECTOR="$_HERE/collect_node.py"
PY="${NODE_PYTHON:-python}"
SSH_USER="${SSH_USER:-}"
TIMEOUT="${TIMEOUT:-6}"
INCOMING="$(cd "$_HERE/../data/incoming" 2>/dev/null && pwd)"
SELF="$(hostname -s 2>/dev/null || hostname)"

if [ -z "$INCOMING" ]; then
  echo "incoming 디렉터리를 찾지 못함 ($_HERE/../data/incoming)" >&2; exit 1
fi
mkdir -p "$INCOMING"

ok=0; fail=0
echo "[$(date +%H:%M:%S)] scan_once: $NODES"
for n in $NODES; do
  if [ "$n" = "$SELF" ] || [ "$n" = "localhost" ]; then
    j="$("$PY" "$COLLECTOR" "$n" 2>/dev/null)"           # master/자기 자신은 로컬 실행
  else
    t="$n"; [ -n "$SSH_USER" ] && t="$SSH_USER@$n"
    j="$(ssh -o BatchMode=yes -o ConnectTimeout="$TIMEOUT" \
            -o StrictHostKeyChecking=accept-new \
            "$t" "$PY '$COLLECTOR' '$n'" 2>/dev/null)"
  fi
  if [ -n "$j" ]; then
    printf '%s' "$j" > "$INCOMING/$n.json"; echo "  $n ✓"; ok=$((ok+1))
  else
    echo "  $n ✗ (ssh/python/collect_node 확인)" >&2; fail=$((fail+1))
  fi
done
echo "  → 성공 $ok / 실패 $fail  (→ $INCOMING)"
