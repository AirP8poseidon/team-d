"""MockCollector — data/sample_*.txt 를 파싱해 노드/잡/헬스로 변환.

결정 5A (파서 입력 가드): 헤더/빈 줄 skip, 칸 수 검증, int() try/except.
잘못된 행은 건너뛰고 경고 로그만 남긴다. 파싱은 절대 예외를 던지지 않으므로
어떤 입력에도 부팅이 멈추지 않는다.
"""
from __future__ import annotations

import logging
import os
from typing import Dict, List

from .base import Collector

logger = logging.getLogger("collectors.mock")

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def _read_rows(filename: str):
    """파일을 읽어 (행번호, 토큰리스트) 를 yield. 헤더·빈 줄은 skip."""
    path = os.path.join(_DATA_DIR, filename)
    if not os.path.exists(path):
        logger.warning("샘플 파일 없음: %s (건너뜀)", path)
        return
    with open(path, "r", encoding="utf-8") as f:
        header_skipped = False
        for lineno, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue  # 빈 줄 skip (행번호와 무관)
            if not header_skipped:
                header_skipped = True
                continue  # 첫 '비어있지 않은' 줄 = 헤더 skip (선행 빈 줄이 있어도 안전)
            yield lineno, line.split()


def _to_int(value: str, lineno: int, field: str):
    """int 변환 실패 시 None 반환 + 경고 (행은 호출 측에서 skip)."""
    try:
        return int(value)
    except (ValueError, TypeError):
        logger.warning("정수 변환 실패 (line %d, %s=%r) — 행 건너뜀", lineno, field, value)
        return None


class MockCollector(Collector):
    """샘플 텍스트 파일 기반 컬렉터 (기본값)."""

    def collect_nodes(self) -> List[Dict]:
        out: List[Dict] = []
        for lineno, cols in _read_rows("sample_sinfo.txt"):
            # NODE STATUS CPU GPU MEM GPU_MODEL  (gpu_model 은 선택)
            if len(cols) < 5:
                logger.warning("sinfo 칸 수 부족 (line %d): %r — 건너뜀", lineno, cols)
                continue
            cpu = _to_int(cols[2], lineno, "cpu")
            gpu = _to_int(cols[3], lineno, "gpu")
            mem = _to_int(cols[4], lineno, "mem")
            if None in (cpu, gpu, mem):
                continue
            out.append({
                "node": cols[0],
                "status": cols[1],
                "cpu": cpu,
                "gpu": gpu,
                "mem": mem,
                "gpu_model": cols[5] if len(cols) > 5 else None,
            })
        return out

    def collect_jobs(self) -> List[Dict]:
        out: List[Dict] = []
        for lineno, cols in _read_rows("sample_squeue.txt"):
            # JOBID USER NODE PURPOSE STATUS ELAPSED
            if len(cols) < 6:
                logger.warning("squeue 칸 수 부족 (line %d): %r — 건너뜀", lineno, cols)
                continue
            out.append({
                "job_id": cols[0],
                "user": cols[1],
                "node": cols[2],
                "purpose": cols[3],
                "status": cols[4],
                "elapsed": cols[5],
            })
        return out

    def collect_health(self) -> List[Dict]:
        out: List[Dict] = []
        for lineno, cols in _read_rows("sample_health.txt"):
            # NODE TEMP DISK_STATUS NFS_STATUS UPDATED_AT
            if len(cols) < 5:
                logger.warning("health 칸 수 부족 (line %d): %r — 건너뜀", lineno, cols)
                continue
            temp = _to_int(cols[1], lineno, "temp")
            if temp is None:
                continue
            out.append({
                "node": cols[0],
                "temp": temp,
                "disk_status": cols[2],
                "nfs_status": cols[3],
                "updated_at": cols[4],
            })
        return out
