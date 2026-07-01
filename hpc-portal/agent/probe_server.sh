#!/usr/bin/env bash
# HPC 서버 정찰 — 각 원격 서버에서 그대로 실행해 출력을 복사해 오면,
# node_report.py(수집 에이전트)를 그 서버 실제 제원에 맞게 조정할 수 있다.
# 읽기 전용 · sudo 불필요 · 설치 없음. 없는 도구는 "(없음)"으로 표기하고 계속 진행.
#
# 사용:
#   bash probe_server.sh                 # 화면 출력
#   bash probe_server.sh > nodeXX.txt    # 파일로 저장해서 가져오기
set +e

line(){ printf '\n=== %s ===\n' "$1"; }
have(){ command -v "$1" >/dev/null 2>&1 && echo yes || echo no; }

printf '############ HPC SERVER PROBE ############\n'
printf 'probe_time: %s\n' "$(date '+%Y-%m-%d %H:%M:%S')"

line "1) 호스트/OS"
echo "hostname    : $(hostname 2>/dev/null)"
echo "hostname -s : $(hostname -s 2>/dev/null)"
echo "uname       : $(uname -a 2>/dev/null)"
if [ -r /etc/os-release ]; then . /etc/os-release 2>/dev/null; echo "os          : $PRETTY_NAME"; else echo "os          : (etc/os-release 없음)"; fi

line "2) Python (에이전트 실행 요건)"
echo "python3 : $(have python3)  $(python3 --version 2>&1)"
echo "python  : $(have python)   $(python --version 2>&1)"

line "3) CPU / 메모리"
echo "nproc       : $(have nproc)  $(nproc 2>/dev/null)"
echo "cpu model   : $(grep -m1 'model name' /proc/cpuinfo 2>/dev/null | cut -d: -f2- | sed 's/^ //')"
echo "/proc/stat  : $([ -r /proc/stat ] && echo readable || echo '(없음 — CPU% 계산 불가)')"
echo "/proc/meminfo:"
grep -E '^(MemTotal|MemAvailable|MemFree):' /proc/meminfo 2>/dev/null | sed 's/^/    /' || echo "    (없음)"
echo "free 명령   : $(have free)"

line "4) GPU (가장 중요 — 제원 좌우)"
echo "nvidia-smi  : $(have nvidia-smi)"
if command -v nvidia-smi >/dev/null 2>&1; then
  echo "  -- GPU 개수/모델 --"
  nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader 2>/dev/null | sed 's/^/    /'
  echo "  -- 에이전트가 쓸 쿼리 샘플(util,temp,name) --"
  nvidia-smi --query-gpu=utilization.gpu,temperature.gpu,name --format=csv,noheader,nounits 2>/dev/null | sed 's/^/    /'
fi
echo "rocm-smi(AMD): $(have rocm-smi)"
echo "sensors(CPU온도): $(have sensors)"
[ "$(have sensors)" = yes ] && sensors 2>/dev/null | grep -iE 'temp|Core' | head -5 | sed 's/^/    /'

line "5) 디스크 / NFS"
echo "df -P / :"; df -P / 2>/dev/null | sed 's/^/    /'
echo "nfs 마운트:"; mount 2>/dev/null | grep -iE 'type nfs| nfs ' | sed 's/^/    /' || true
[ -z "$(mount 2>/dev/null | grep -iE 'type nfs| nfs ')" ] && echo "    (nfs 마운트 안 보임)"
echo "nfsstat 명령: $(have nfsstat)"

line "6) 스케줄러 (있으면 추후 보강 가능)"
echo "SLURM squeue/sinfo : $(have squeue) / $(have sinfo)"
echo "PBS qstat/pbsnodes : $(have qstat) / $(have pbsnodes)"
[ "$(have sinfo)" = yes ] && { echo "  -- sinfo 샘플 --"; sinfo 2>/dev/null | head -5 | sed 's/^/    /'; }

line "7) 실행 중 작업 (mpirun 직접 실행 탐지 가능 여부)"
echo "ps -eo 지원: $(have ps)"
if command -v ps >/dev/null 2>&1; then
  echo "  -- mpirun/mpiexec 프로세스(있으면) --"
  ps -eo user=,etime=,args= 2>/dev/null | awk '{for(i=3;i<=NF;i++){n=split($i,a,"/"); if(a[n]=="mpirun"||a[n]=="mpiexec"){print "    "$0; break}}}' | head -5
  echo "  -- 상위 CPU 프로세스 5개(참고) --"
  ps -eo pcpu,user,args 2>/dev/null --sort=-pcpu | head -6 | sed 's/^/    /'
fi

line "8) 포털 호스트 접속 가능? (이 노드 → 워크스테이션 10.10.9.101:22)"
PORTAL_HOST="${PORTAL_HOST:-10.10.9.101}"
if command -v nc >/dev/null 2>&1; then
  nc -z -w 3 "$PORTAL_HOST" 22 2>/dev/null && echo "  nc: $PORTAL_HOST:22 연결 가능 ✅" || echo "  nc: $PORTAL_HOST:22 연결 불가 ❌ (같은 망/VPN/방화벽 확인)"
else
  echo "  nc 없음 — 수동 확인: ssh mac-leesh@$PORTAL_HOST"
fi
echo "scp 명령: $(have scp)  / ssh: $(have ssh)"

printf '\n############ END PROBE ############\n'
