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


def test_stats_usage_core_and_extensions():
    with TestClient(main.app) as client:
        r = client.get("/api/stats/usage")
        assert r.status_code == 200
        u = r.json()
        # SPEC 핵심 키
        assert {"by_node", "by_user", "trend"} <= set(u)
        assert all(set(x) == {"node", "gpu_hours"} for x in u["by_node"])
        # 확장(FR-S3)
        assert {"summary", "stacked"} <= set(u)
        assert {"total", "avgPerDay", "activeUsers", "activeNodes"} <= set(u["summary"])
        assert "nodes" in u["stacked"] and "series" in u["stacked"]
