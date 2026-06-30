"""컬렉터 팩토리 — 수집 seam 의 진입점.

get_collector(name) 으로 컬렉터를 고른다. 기본은 "mock" (샘플 파일 파싱).
실서버 연동은 여기 TODO 훅에 slurm/prometheus 를 등록하면 된다.
환경변수 COLLECTOR 로 main.py 가 이름을 넘긴다.
"""
from __future__ import annotations

from .base import Collector
from .mock import MockCollector


def get_collector(name: str) -> Collector:
    """이름으로 컬렉터 인스턴스를 반환. 알 수 없으면 mock 으로 폴백."""
    key = (name or "mock").strip().lower()
    if key == "mock":
        return MockCollector()
    if key == "ingest":
        # push 형: 각 서버가 data/incoming/<node>.json 으로 밀어 넣음 (결정 A)
        from .ingest import IngestCollector
        return IngestCollector()
    # TODO(실연동): "slurm" -> SlurmCollector()  (collectors/slurm.py)
    #   from .slurm import SlurmCollector; return SlurmCollector()
    # TODO(실연동): "prometheus" -> PrometheusCollector()  (collectors/prometheus.py)
    #   from .prometheus import PrometheusCollector; return PrometheusCollector()
    import logging
    logging.getLogger("collectors").warning(
        "알 수 없는 컬렉터 %r — MockCollector 로 폴백", name)
    return MockCollector()


__all__ = ["Collector", "MockCollector", "get_collector"]
