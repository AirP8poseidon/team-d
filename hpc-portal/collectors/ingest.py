"""IngestCollector — push 형 수집 (결정 A 실연동 경로).

각 계산 서버가 자기 정보를 JSON 으로 만들어 scp/ssh 로 이 포털 호스트의
data/incoming/<node>.json 으로 밀어 넣으면, 이 컬렉터가 그 파일들을 읽어
nodes/jobs/health 로 반영한다. main.py·라우터·DB 스키마 변경 불필요.

켜기:  COLLECTOR=ingest uvicorn main:app
셀프테스트:  python -m collectors.ingest   (또는 python collectors/ingest.py)

안전장치:
- 어떤 파일이 깨졌거나 incoming 이 비어도 예외를 던지지 않는다 (결정 5A).
- 유효 리포트가 하나도 없으면 MockCollector 로 폴백 (데모가 빈 화면이 안 되게).
- node 값은 db.NODES(node01..node08) 안의 것만 받는다.

JSON 포맷 (노드당 1파일, data/incoming/<node>.json):
{
  "node": "node01",
  "ts": "2026-06-30T16:30:00",          # 선택. 없으면 수신 시각
  "status": "alloc",                     # 선택. 없으면 'idle'
  "cpu": 45, "gpu": 10, "mem": 38,       # 정수 %, 없으면 0
  "gpu_model": "A100",                   # 선택
  "temp": 42,                            # 온도(℃), 없으면 0
  "disk_status": "ok", "nfs_status": "ok",
  "jobs": [                              # 선택. 이 노드에서 도는 작업(mpirun 포함)
    {"job_id":"mpi-1","user":"kim","purpose":"mpirun deep-learning",
     "status":"RUNNING","elapsed":"02:10","source":"mpirun"}
  ]
}
"""
from __future__ import annotations

import glob
import json
import logging
import os
from datetime import datetime
from typing import Dict, List

from .base import Collector
from .mock import MockCollector

try:  # 통합 키 — db 와 동일 집합 사용
    from db import NODES
except Exception:  # pragma: no cover - db 임포트 불가 시 폴백
    NODES = [f"node{i:02d}" for i in range(1, 9)]

logger = logging.getLogger("collectors.ingest")

_DEFAULT_INCOMING = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "incoming"
)
# 테스트/배치는 HPC_INCOMING_DIR 로 경로 변경 가능
INCOMING_DIR = os.environ.get("HPC_INCOMING_DIR", _DEFAULT_INCOMING)


def _to_int(value, default: int = 0) -> int:
    """정수 변환 실패 시 default (절대 raise 안 함 — 결정 5A)."""
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _read_reports() -> List[Dict]:
    """incoming/*.json 을 읽어 유효한 노드 리포트 리스트 반환. 절대 raise 안 함.

    - 깨진 JSON 파일은 건너뛰고 경고만.
    - node 가 NODES(node01..08) 밖이면 건너뜀(통합 키 보호).
    - 파일 1개가 dict(노드 1개) 또는 list(여러 노드) 둘 다 허용.
    """
    reports: List[Dict] = []
    if not os.path.isdir(INCOMING_DIR):
        return reports
    for path in sorted(glob.glob(os.path.join(INCOMING_DIR, "*.json"))):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:
            logger.warning("리포트 읽기 실패 %s — 건너뜀 (%s)", path, exc)
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            node = str(item.get("node", "")).strip()
            if node not in NODES:
                logger.warning("알 수 없는 node %r (%s) — 건너뜀", node, os.path.basename(path))
                continue
            reports.append(item)
    return reports


class IngestCollector(Collector):
    """data/incoming/<node>.json (각 서버가 push) 를 읽는 컬렉터."""

    def __init__(self) -> None:
        # 리포트가 없을 때 빈 화면 대신 mock 으로 폴백 (데모 안전)
        self._fallback = MockCollector()

    def collect_nodes(self) -> List[Dict]:
        reports = _read_reports()
        if not reports:
            logger.info("incoming 비어있음 — nodes mock 폴백")
            return self._fallback.collect_nodes()
        out: List[Dict] = []
        for r in reports:
            out.append({
                "node": r["node"],
                "status": str(r.get("status") or "idle"),
                "cpu": _to_int(r.get("cpu")),
                "gpu": _to_int(r.get("gpu")),
                "mem": _to_int(r.get("mem")),
                "gpu_model": str(r.get("gpu_model") or ""),
            })
        return out

    def collect_health(self) -> List[Dict]:
        reports = _read_reports()
        if not reports:
            return self._fallback.collect_health()
        now = datetime.now().isoformat()
        out: List[Dict] = []
        for r in reports:
            out.append({
                "node": r["node"],
                "temp": _to_int(r.get("temp")),
                "disk_status": str(r.get("disk_status") or "unknown"),
                "nfs_status": str(r.get("nfs_status") or "unknown"),
                "updated_at": str(r.get("ts") or now),
            })
        return out

    def collect_jobs(self) -> List[Dict]:
        reports = _read_reports()
        if not reports:
            return self._fallback.collect_jobs()
        out: List[Dict] = []
        for r in reports:
            node = r["node"]
            jobs = r.get("jobs") or []
            if not isinstance(jobs, list):
                continue
            for i, j in enumerate(jobs):
                if not isinstance(j, dict):
                    continue
                out.append({
                    "job_id": str(j.get("job_id") or f"{node}-{i + 1}"),
                    "user": str(j.get("user") or "?"),
                    "node": node,
                    "purpose": str(j.get("purpose") or ""),
                    "status": str(j.get("status") or "RUNNING"),
                    "elapsed": str(j.get("elapsed") or ""),
                })
        return out


if __name__ == "__main__":  # 셀프테스트 (드라이런)
    logging.basicConfig(level=logging.INFO)
    c = IngestCollector()
    reps = _read_reports()
    print(f"[ingest selftest] INCOMING_DIR = {INCOMING_DIR}")
    print(f"  유효 리포트 {len(reps)}개  노드: {[r.get('node') for r in reps]}")
    print(f"  collect_nodes  -> {len(c.collect_nodes())} rows")
    print(f"  collect_jobs   -> {len(c.collect_jobs())} rows")
    print(f"  collect_health -> {len(c.collect_health())} rows")
    if not reps:
        print("  (리포트 없음 → MockCollector 폴백 동작 중)")
