#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""노드 자원 1회 수집 → JSON(stdout). 이 클러스터용(RHEL7, python3 없음).

python 2.7 / 3 양쪽에서 동작하며 표준 라이브러리만 쓴다. GPU 없는 CPU 클러스터라
GPU 필드는 0/"CPU"로 두고, 실행 중인 계산 작업(pschism/padcirc/nemo/swan 등)을
ps 의 상위 CPU 프로세스에서 뽑아 "현재 작업(누가·무슨 모델)"으로 보고한다.

사용:
  python collect_node.py [node명]      # 기본: hostname -s
  (scan_push.sh 가 각 노드에서 ssh로 이걸 실행해 JSON 을 받아감)
"""
from __future__ import print_function
import json
import re
import socket
import subprocess
import sys
import time


def _sh(cmd):
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, _ = p.communicate()
        if isinstance(out, bytes):
            out = out.decode("utf-8", "replace")
        return out or ""
    except Exception:
        return ""


def cpu_pct():
    """CPU 사용률 % (/proc/stat 2회 샘플). 실패 시 0."""
    def snap():
        try:
            with open("/proc/stat") as f:
                v = [int(x) for x in f.readline().split()[1:]]
            idle = v[3] + (v[4] if len(v) > 4 else 0)
            return sum(v), idle
        except Exception:
            return None
    a = snap()
    if not a:
        return 0
    time.sleep(0.3)
    b = snap()
    if not b or b[0] == a[0]:
        return 0
    busy = (b[0] - a[0]) - (b[1] - a[1])
    return max(0, min(100, int(busy * 100 / (b[0] - a[0]))))


def mem_pct():
    """메모리 사용률 % (MemAvailable 기반). 실패 시 0."""
    try:
        d = {}
        with open("/proc/meminfo") as f:
            for ln in f:
                k, _, v = ln.partition(":")
                d[k.strip()] = int(v.split()[0])
        total = d.get("MemTotal", 0)
        avail = d.get("MemAvailable", d.get("MemFree", 0))
        return max(0, min(100, int((total - avail) * 100 / total))) if total else 0
    except Exception:
        return 0


def disk_status():
    out = _sh(["df", "-P", "/"]).splitlines()
    if len(out) < 2:
        return "unknown"
    try:
        pct = int(out[1].split()[4].rstrip("%"))
    except Exception:
        return "unknown"
    return "critical" if pct >= 97 else ("warning" if pct >= 90 else "ok")


def nfs_status():
    return "ok" if "type nfs" in _sh(["mount"]) else "none"


def temp_c():
    m = re.search(r"(?:Tctl|Tdie|Package id 0|Core 0)[^+]*\+([0-9]+)", _sh(["sensors"]))
    return int(m.group(1)) if m else 0


# 시스템 계정 — "현재 작업"에서 제외
_SKIP = set(["root", "gdm", "dbus", "polkitd", "rpc", "rpcuser", "chrony",
             "nobody", "postfix", "colord", "libstoragemgmt"])


def jobs(node):
    """상위 CPU 프로세스에서 실제 계산 작업 추출 (>50% CPU, 시스템계정 제외, 최대 3개)."""
    out = _sh(["ps", "-eo", "pcpu=,user=,comm=,args=", "--sort=-pcpu"])
    res = []
    for i, ln in enumerate(out.splitlines()):
        parts = ln.split(None, 3)
        if len(parts) < 3:
            continue
        pcpu, user, comm = parts[0], parts[1], parts[2]
        args = parts[3] if len(parts) > 3 else comm
        try:
            if float(pcpu) < 50:
                break  # 정렬돼 있으니 이하로는 볼 필요 없음
        except ValueError:
            continue
        if user in _SKIP:
            continue
        purpose = args.strip()[:70]
        res.append({
            "job_id": "%s-%d" % (node, i),
            "user": user,
            "purpose": purpose,
            "status": "RUNNING",
            "elapsed": "",
            "source": "ps",
        })
        if len(res) >= 3:
            break
    return res


def main():
    node = sys.argv[1] if len(sys.argv) > 1 else socket.gethostname().split(".")[0]
    c = cpu_pct()
    js = jobs(node)
    rep = {
        "node": node,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "status": "alloc" if (c > 20 or js) else "idle",
        "cpu": c,
        "gpu": 0,            # CPU 클러스터 — GPU 없음
        "mem": mem_pct(),
        "gpu_model": "CPU",
        "temp": temp_c(),
        "disk_status": disk_status(),
        "nfs_status": nfs_status(),
        "jobs": js,
    }
    sys.stdout.write(json.dumps(rep, ensure_ascii=False))


if __name__ == "__main__":
    main()
