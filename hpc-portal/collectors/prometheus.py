"""PrometheusCollector — 실 메트릭 연동 drop-in 자리 (미구현).

실연동 접근:
- Prometheus HTTP API `GET /api/v1/query?query=<PromQL>` 로 메트릭 조회.
  예) node CPU:    100 - avg by(instance)(rate(node_cpu_seconds_total{mode="idle"}[1m]))*100
      GPU 사용률:  DCGM_FI_DEV_GPU_UTIL
      온도:        node_hwmon_temp_celsius  (collect_health 의 temp)
      디스크:      node_filesystem_avail_bytes 기준 임계 판정 -> disk_status
- instance 라벨을 node01..node08 로 매핑 (relabel 또는 조회 후 변환).

requests/httpx 로 호출. Collector ABC 인터페이스만 맞추면 drop-in 교체된다.
"""
from __future__ import annotations

from typing import Dict, List

from .base import Collector


class PrometheusCollector(Collector):
    def __init__(self, base_url: str = "http://localhost:9090"):
        self.base_url = base_url

    def collect_nodes(self) -> List[Dict]:
        raise NotImplementedError("PrometheusCollector 미구현 — /api/v1/query 연동 필요")

    def collect_jobs(self) -> List[Dict]:
        raise NotImplementedError("잡 정보는 SLURM 소관 — SlurmCollector 사용")

    def collect_health(self) -> List[Dict]:
        raise NotImplementedError("PrometheusCollector 미구현 — /api/v1/query 연동 필요")
