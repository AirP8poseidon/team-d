"""
[팀원2] pytest 최소 세트 — SPEC §13 6A.

(1) 파서 정상/깨진 행  (2) 멱등 시드 2회 → 행수 동일
(3) node01~08 전 테이블 정합  (4) 각 라우터 TestClient 200 스모크.
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from routers import stats, system

NODES = {f"node{i:02d}" for i in range(1, 9)}


# (1) 파서 — 헤더/빈줄/짧은행/잘못된 int 는 건너뛰고, 정상 행만 반환(부팅 무중단)
def test_parser_skips_header_and_broken_rows():
    lines = [
        "NODE TEMP DISK_STATUS NFS_STATUS UPDATED_AT",   # 헤더
        "",                                              # 빈 줄
        "node01 42 ok ok 2026-06-30T14:00:00",           # 정상
        "node02 bad ok ok 2026-06-30T14:00:00",          # temp 비정수 → skip
        "node03 55 warning",                             # 칸 부족(3) → skip
        "node04 60 ok down",                             # 정상(updated_at 생략)
    ]
    rows = system.parse_health_lines(lines)
    assert [r["node"] for r in rows] == ["node01", "node04"]
    assert rows[0]["temp"] == 42
    assert rows[1]["nfs_status"] == "down"
    assert rows[1]["updated_at"] is None


# (2) 멱등 시드 — 두 번째 호출은 추가 없이 행수 동일
def test_idempotent_seed():
    def count(get_db, table):
        c = get_db()
        n = c.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()["c"]
        c.close()
        return n

    stats.seed()                                   # 이미 import 시 시드됨 → 추가 0
    u1 = count(stats.get_db, "usage_log")
    stats.seed()
    u2 = count(stats.get_db, "usage_log")
    assert u1 == u2 and u1 > 0

    system.load_health()
    h1 = count(system.get_db, "node_health")
    system.load_health()
    h2 = count(system.get_db, "node_health")
    assert h1 == h2 == 8


# (3) 노드 키 정합 — 전 테이블 node01~08
def test_node_keys_consistent():
    c = system.get_db()
    health_nodes = {r["node"] for r in c.execute("SELECT node FROM node_health")}
    c.close()
    assert health_nodes == NODES

    c = stats.get_db()
    usage_nodes = {r["node"] for r in c.execute("SELECT DISTINCT node FROM usage_log")}
    c.close()
    assert usage_nodes <= NODES


# (4) TestClient 200 스모크 + 응답 스키마(SPEC §7.4)
def _client():
    app = FastAPI()
    app.include_router(system.router)
    app.include_router(stats.router)
    return TestClient(app)


def test_endpoints_200_and_schema():
    c = _client()

    r = c.get("/api/system/health")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 8
    assert set(data[0]) == {"node", "temp", "disk_status", "nfs_status", "updated_at"}

    r = c.get("/api/system/history")
    assert r.status_code == 200
    assert {"labels", "avg", "max"} <= set(r.json())

    r = c.get("/api/stats/usage")
    assert r.status_code == 200
    body = r.json()
    assert {"by_node", "by_user", "trend"} <= set(body)
    assert all(set(x) == {"node", "gpu_hours"} for x in body["by_node"])
