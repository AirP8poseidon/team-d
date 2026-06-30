"""[팀원2] 확장 엔드포인트 테스트 — /api/system/history + /api/stats/usage 확장 필드.

팀장 스모크(6A)에 더해, 팀원2가 추가한 온도 추이·요약·구성 응답을 검증.
conftest 가 임시 DB를 강제하고, TestClient with 블록이 lifespan(컬렉터 적재)을 실행한다.
"""
from starlette.testclient import TestClient

import main


def test_system_health_schema_and_history():
    with TestClient(main.app) as client:
        r = client.get("/api/system/health")
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 1
        assert set(data[0]) == {"node", "temp", "disk_status", "nfs_status", "updated_at"}

        r = client.get("/api/system/history")
        assert r.status_code == 200
        h = r.json()
        assert {"labels", "avg", "max"} <= set(h)
        assert len(h["labels"]) == len(h["avg"]) == len(h["max"])

        # 노드별 네트워크 상태(확장) — node01..08, 스키마 정합
        r = client.get("/api/system/network")
        assert r.status_code == 200
        net = r.json()
        assert len(net) == 8
        assert set(net[0]) == {"node", "rx_mbps", "tx_mbps", "latency_ms", "link_up", "updated_at"}

        # 서버(노드)별 디스크 용량(확장) — 스키마·사용률 정합
        r = client.get("/api/system/disk")
        assert r.status_code == 200
        disk = r.json()
        assert len(disk) == 8
        assert set(disk[0]) == {"node", "used_gb", "total_gb", "used_pct", "updated_at"}
        for d in disk:
            assert 0 <= d["used_gb"] <= d["total_gb"]      # 사용량은 총량 이내
            assert abs(d["used_pct"] - round(d["used_gb"] / d["total_gb"] * 100, 1)) < 0.1


def test_stats_usage_core_and_extensions():
    with TestClient(main.app) as client:
        r = client.get("/api/stats/usage")
        assert r.status_code == 200
        u = r.json()
        # SPEC 핵심 키
        assert {"by_node", "by_user", "trend"} <= set(u)
        assert all(set(x) == {"node", "gpu_hours"} for x in u["by_node"])
        assert "summary" in u
        assert {"total", "avgPerDay", "activeUsers", "activeNodes"} <= set(u["summary"])
        assert len(u["trend"]) >= 7   # 추이 1주일 이전부터

        # 스토리지 용량 체크(기준 시점별 스냅샷, GB)
        r = client.get("/api/stats/capacity")
        assert r.status_code == 200
        cap = r.json()["references"]
        assert {ref["key"] for ref in cap} == {"w1", "d3", "today", "now"}
        for ref in cap:
            assert {"key", "label", "cutoff", "users"} <= set(ref)
            assert all(set(x) == {"user", "used_gb", "quota_gb", "used_pct"} for x in ref["users"])
        tot = {ref["key"]: sum(x["used_gb"] for x in ref["users"]) for ref in cap}
        assert tot["now"] >= tot["w1"]   # 스토리지는 증가 경향 → 현재가 1주일전 이상
        # 사용률 = used/quota 정합 + 사용률 내림차순 정렬
        for ref in cap:
            for x in ref["users"]:
                assert abs(x["used_pct"] - round(x["used_gb"] / x["quota_gb"] * 100, 1)) < 0.1
            pcts = [x["used_pct"] for x in ref["users"]]
            assert pcts == sorted(pcts, reverse=True)
