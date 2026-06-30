"""SlurmCollector — 실 SLURM 연동 drop-in 자리 (미구현).

실연동 접근:
- collect_jobs():  `squeue --noheader -o '%i %u %N %j %T %M'` 를 subprocess 로 실행,
  공백 분리해 jobs dict 로 매핑. (mock.py 의 파서 가드를 그대로 재사용 권장.)
- collect_nodes(): `sinfo --noheader -o '%n %t %C %G %m'` 출력 파싱.
  CPU/GPU 사용률은 sinfo 로는 부족하므로 scontrol show node 또는 Prometheus 보강.
- collect_health(): SLURM 범위 밖. PrometheusCollector 또는 node_exporter 사용.

Collector ABC 의 인터페이스만 맞추면 main.py 변경 없이 교체된다.
"""
from __future__ import annotations

from typing import Dict, List

from .base import Collector


class SlurmCollector(Collector):
    def collect_nodes(self) -> List[Dict]:
        raise NotImplementedError("SlurmCollector 미구현 — sinfo subprocess 연동 필요")

    def collect_jobs(self) -> List[Dict]:
        raise NotImplementedError("SlurmCollector 미구현 — squeue subprocess 연동 필요")

    def collect_health(self) -> List[Dict]:
        raise NotImplementedError("헬스는 SLURM 범위 밖 — PrometheusCollector 사용")
