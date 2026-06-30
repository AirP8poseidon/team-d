"""파서 테스트 (결정 5A) — 정상 파싱 + 깨진 행 skip(예외 없음)."""
import os

from collectors.mock import MockCollector
from collectors import mock as mock_mod


def test_parses_valid_samples():
    c = MockCollector()
    nodes = c.collect_nodes()
    jobs = c.collect_jobs()
    health = c.collect_health()
    assert len(nodes) == 8
    assert len(jobs) == 8
    assert len(health) == 8
    # 컬럼 매핑 확인
    assert set(nodes[0].keys()) == {"node", "status", "cpu", "gpu", "mem", "gpu_model"}
    assert isinstance(nodes[0]["cpu"], int)
    assert set(jobs[0].keys()) == {"job_id", "user", "node", "purpose", "status", "elapsed"}


def test_malformed_lines_are_skipped(tmp_path, monkeypatch):
    """깨진 행(칸 부족·정수 아님)을 섞어도 예외 없이 정상 행만 반환."""
    bad = tmp_path / "sample_sinfo.txt"
    bad.write_text(
        "NODE STATUS CPU GPU MEM GPU_MODEL\n"
        "node01 idle 12 0 22 A100\n"      # 정상
        "\n"                                # 빈 줄
        "node02 idle oops 0 22 A100\n"     # cpu 정수 아님 -> skip
        "node03 alloc 50\n"                # 칸 부족 -> skip
        "node04 alloc 84 91 76 A100\n",    # 정상
        encoding="utf-8",
    )
    # 데이터 디렉터리를 임시 폴더로 우회
    monkeypatch.setattr(mock_mod, "_DATA_DIR", str(tmp_path))

    nodes = MockCollector().collect_nodes()  # 예외가 나면 테스트 실패
    names = [n["node"] for n in nodes]
    assert names == ["node01", "node04"]
