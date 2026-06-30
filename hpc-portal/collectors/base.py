"""데이터 수집 인터페이스 (수집 seam).

모든 컬렉터는 이 ABC 를 구현한다. 현재는 MockCollector(샘플 파일 파싱)만
구현돼 있고, 실서버 연동은 SlurmCollector / PrometheusCollector 가 같은
인터페이스를 drop-in 으로 구현하면 된다 (main.py·라우터 변경 불필요).
"""
from __future__ import annotations

import abc
from typing import Dict, List


class Collector(abc.ABC):
    """노드/잡/헬스 데이터를 수집하는 추상 인터페이스.

    반환 dict 의 키는 DB 컬럼명과 1:1 로 맞춘다:
      - collect_nodes()  -> [{node, status, cpu, gpu, mem, gpu_model}]
      - collect_jobs()   -> [{job_id, user, node, purpose, status, elapsed}]
      - collect_health() -> [{node, temp, disk_status, nfs_status, updated_at}]

    구현체는 어떤 입력에도 예외를 던지지 않아야 한다 (결정 5A: 부팅 무중단).
    """

    @abc.abstractmethod
    def collect_nodes(self) -> List[Dict]:
        raise NotImplementedError

    @abc.abstractmethod
    def collect_jobs(self) -> List[Dict]:
        raise NotImplementedError

    @abc.abstractmethod
    def collect_health(self) -> List[Dict]:
        raise NotImplementedError
