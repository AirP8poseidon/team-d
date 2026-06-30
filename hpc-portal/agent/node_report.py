#!/usr/bin/env python3
"""HPC 노드 → 포털 푸시 에이전트 (각 계산 서버에 두고 실행).

로컬 자원 정보(GPU 사용률·온도·모델, CPU/MEM, 디스크, NFS, mpirun 직접 실행 작업)를
JSON 으로 만들어 scp 로 포털 호스트의 data/incoming/<node>.json 에 밀어 넣는다.
포털은 COLLECTOR=ingest 로 그 파일을 읽어 대시보드에 반영한다.

이 스크립트는 표준 라이브러리만 쓰며, 도구(nvidia-smi 등)가 없으면 0/기본값으로
우아하게 degrade 한다 — GPU 없는 머신(맥 포함)에서도 그대로 돈다(루프백 테스트용).

사용 예:
  # 1회 푸시 (비밀번호 또는 SSH 키 인증)
  python3 node_report.py --portal-host 10.10.9.101 --portal-user mac-leesh --node node01

  # 5초 루프
  python3 node_report.py --portal-host 10.10.9.101 --portal-user mac-leesh \
      --node node01 --loop --interval 5

  # 전송 없이 JSON 만 파일로 (테스트)
  python3 node_report.py --node node01 --out /tmp/node01.json

환경변수로도 설정 가능: PORTAL_HOST, PORTAL_USER, PORTAL_INCOMING, NODE, INTERVAL.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime

DEFAULT_INCOMING = "Develop/Projects/GEOSR_hackton/team-d/hpc-portal/data/incoming"


def _run(cmd):
    """명령 실행 → stdout 문자열. 실패/부재 시 빈 문자열 (절대 raise 안 함)."""
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        return out.stdout or ""
    except Exception:
        return ""


def _has(tool: str) -> bool:
    return shutil.which(tool) is not None


def collect_gpu():
    """(util%, temp℃, model) — nvidia-smi 첫 GPU 기준. 없으면 (0,0,'N/A')."""
    if not _has("nvidia-smi"):
        return 0, 0, "N/A"
    line = _run([
        "nvidia-smi",
        "--query-gpu=utilization.gpu,temperature.gpu,name",
        "--format=csv,noheader,nounits",
    ]).strip().splitlines()
    if not line:
        return 0, 0, "GPU"
    parts = [p.strip() for p in line[0].split(",")]
    util = int(float(parts[0])) if len(parts) > 0 and parts[0].replace(".", "").isdigit() else 0
    temp = int(float(parts[1])) if len(parts) > 1 and parts[1].replace(".", "").isdigit() else 0
    model = parts[2] if len(parts) > 2 and parts[2] else "GPU"
    return util, temp, model


def collect_cpu_pct() -> int:
    """CPU 사용률 % (1 - idle). Linux /proc/stat 2회 샘플; 실패 시 0."""
    def snap():
        try:
            with open("/proc/stat") as f:
                vals = [int(x) for x in f.readline().split()[1:]]
            idle = vals[3] + (vals[4] if len(vals) > 4 else 0)
            return sum(vals), idle
        except Exception:
            return None
    a = snap()
    if a is None:
        # 비-Linux(맥 등): uptime load 로 근사 불가 → 0
        return 0
    time.sleep(0.2)
    b = snap()
    if b is None or b[0] == a[0]:
        return 0
    busy = (b[0] - a[0]) - (b[1] - a[1])
    return max(0, min(100, int(busy / (b[0] - a[0]) * 100)))


def collect_mem_pct() -> int:
    """메모리 사용률 % (MemAvailable 기반). Linux /proc/meminfo; 실패 시 0."""
    try:
        info = {}
        with open("/proc/meminfo") as f:
            for ln in f:
                k, _, v = ln.partition(":")
                info[k.strip()] = int(v.strip().split()[0])
        total = info.get("MemTotal", 0)
        avail = info.get("MemAvailable", info.get("MemFree", 0))
        if total <= 0:
            return 0
        return max(0, min(100, int((total - avail) / total * 100)))
    except Exception:
        return 0


def collect_disk_status() -> str:
    """루트 fs 사용률 → ok/warning/critical."""
    out = _run(["df", "-P", "/"]).splitlines()
    if len(out) < 2:
        return "unknown"
    try:
        pct = int(out[1].split()[4].rstrip("%"))
    except Exception:
        return "unknown"
    if pct >= 97:
        return "critical"
    if pct >= 90:
        return "warning"
    return "ok"


def collect_nfs_status() -> str:
    """NFS 마운트 유무 → ok/none."""
    mounts = _run(["mount"])
    if " type nfs" in mounts or " nfs " in mounts or "(nfs" in mounts:
        return "ok"
    return "none"


def collect_mpirun_jobs(node: str):
    """스케줄러 큐에 안 잡히는 mpirun 직접 실행 작업 탐지 (ps)."""
    jobs = []
    out = _run(["ps", "-eo", "user=,etime=,args="])
    for i, ln in enumerate(out.splitlines()):
        parts = ln.split(None, 2)
        if len(parts) < 3:
            continue
        user, etime, args = parts[0], parts[1], parts[2]
        toks = args.split()
        # 실행파일명이 정확히 mpirun/mpiexec 인 토큰이 있어야 매칭
        # ('mpirun' 문자열이 경로 일부에 들어간 무관한 프로세스 오탐 방지)
        if not any(os.path.basename(t) in ("mpirun", "mpiexec") for t in toks):
            continue
        purpose = args.strip()[:80].replace('"', "'")
        jobs.append({
            "job_id": f"mpi-{node}-{i}",
            "user": user,
            "purpose": purpose,
            "status": "RUNNING",
            "elapsed": etime,
            "source": "mpirun",
        })
    return jobs


def build_report(node: str) -> dict:
    gpu_util, gpu_temp, gpu_model = collect_gpu()
    cpu = collect_cpu_pct()
    jobs = collect_mpirun_jobs(node)
    # 활동 여부로 status 추정
    status = "alloc" if (gpu_util > 5 or cpu > 20 or jobs) else "idle"
    return {
        "node": node,
        "ts": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "status": status,
        "cpu": cpu,
        "gpu": gpu_util,
        "mem": collect_mem_pct(),
        "gpu_model": gpu_model,
        "temp": gpu_temp,
        "disk_status": collect_disk_status(),
        "nfs_status": collect_nfs_status(),
        "jobs": jobs,
    }


def push(report: dict, host: str, user: str, incoming: str) -> bool:
    """JSON 을 임시파일로 쓰고 scp 로 포털 incoming/ 에 전송."""
    node = report["node"]
    tmp = os.path.join("/tmp", f"{node}.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False)
    dest = f"{user}@{host}:{incoming}/{node}.json"
    rc = subprocess.run(
        ["scp", "-q", "-o", "StrictHostKeyChecking=accept-new", tmp, dest]
    ).returncode
    ts = datetime.now().strftime("%H:%M:%S")
    if rc == 0:
        print(f"[{ts}] pushed {node} -> {host}")
        return True
    print(f"[{ts}] push 실패(scp rc={rc}) — SSH 키/경로/호스트 확인", file=sys.stderr)
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description="HPC 노드 → 포털 푸시 에이전트")
    ap.add_argument("--portal-host", default=os.environ.get("PORTAL_HOST", "10.10.9.101"))
    ap.add_argument("--portal-user", default=os.environ.get("PORTAL_USER", "mac-leesh"))
    ap.add_argument("--incoming", default=os.environ.get("PORTAL_INCOMING", DEFAULT_INCOMING))
    ap.add_argument("--node", default=os.environ.get("NODE", socket.gethostname().split(".")[0]))
    ap.add_argument("--interval", type=int, default=int(os.environ.get("INTERVAL", "5")))
    ap.add_argument("--loop", action="store_true", help="interval 마다 반복 푸시")
    ap.add_argument("--out", help="scp 대신 이 파일로 JSON 만 저장(테스트)")
    ap.add_argument("--stdout", action="store_true",
                    help="scp 대신 JSON 을 표준출력으로 (scan_cluster.sh 가 SSH로 받아감)")
    args = ap.parse_args()

    def one():
        rep = build_report(args.node)
        if args.stdout:
            sys.stdout.write(json.dumps(rep, ensure_ascii=False))
            return True
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(rep, f, ensure_ascii=False, indent=2)
            print(f"wrote {args.out}: {json.dumps(rep, ensure_ascii=False)}")
            return True
        return push(rep, args.portal_host, args.portal_user, args.incoming)

    if args.loop:
        target = args.out or f"{args.portal_user}@{args.portal_host}"
        print(f"loop: {args.node} -> {target} every {args.interval}s (Ctrl+C 종료)")
        try:
            while True:
                one()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n종료")
        return 0
    return 0 if one() else 1


if __name__ == "__main__":
    raise SystemExit(main())
