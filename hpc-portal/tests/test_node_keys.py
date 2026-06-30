"""노드 키 정합 테스트 (결정 6A / T8) — 전 테이블 node 값이 node01..08 안에 있는지.

통합 실패 모드(노드 키 불일치)에 대한 유일한 안전망.
"""
import db
from collectors.mock import MockCollector


def _populate():
    """init + seed + 컬렉터 적재 + node_usage 한 건 등록."""
    db.init_db()
    db.seed_if_empty()
    c = MockCollector()
    db.upsert_nodes(c.collect_nodes())
    db.upsert_jobs(c.collect_jobs())
    db.upsert_health(c.collect_health())
    conn = db.get_db()
    try:
        conn.execute(
            "INSERT INTO node_usage (node, user, purpose, eta, source, created_at) "
            "VALUES (?,?,?,?,?,?)",
            ("node04", "kim", "mpirun 딥러닝", "18:00", "mpirun", "2026-06-30T15:00:00"),
        )
        conn.commit()
    finally:
        conn.close()


def test_all_node_values_within_NODES():
    _populate()
    allowed = set(db.NODES)
    assert allowed == {f"node{i:02d}" for i in range(1, 9)}

    conn = db.get_db()
    try:
        for table in ["nodes", "node_health", "jobs", "node_usage", "usage_log"]:
            rows = conn.execute(f"SELECT DISTINCT node FROM {table}").fetchall()
            for r in rows:
                assert r["node"] in allowed, f"{table} 에 허용되지 않은 노드 키: {r['node']}"
    finally:
        conn.close()
