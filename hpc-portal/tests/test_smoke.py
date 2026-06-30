"""스모크 테스트 (결정 6A) — 각 엔드포인트가 TestClient 로 200 응답."""
from starlette.testclient import TestClient

import main


def test_endpoints_return_200():
    # TestClient 의 with 블록이 startup/shutdown(컬렉터 적재 포함)을 실행
    with TestClient(main.app) as client:
        gets = [
            "/",
            "/api/monitoring/nodes",
            "/api/monitoring/jobs",
            "/api/monitoring/usage",
            "/api/monitoring/usage/latest",
            "/api/wiki/servers",
            "/api/wiki/posts",
            "/api/wiki/posts?q=sbatch",
            "/api/chat/messages",
            "/api/chat/messages?after=0",
            "/api/stats/usage",
            "/api/system/health",
        ]
        for path in gets:
            r = client.get(path)
            assert r.status_code == 200, f"GET {path} -> {r.status_code}"

        # POST node_usage -> 등록 후 카드(latest)에 반영
        r = client.post("/api/monitoring/usage", json={
            "node": "node04", "user": "kim",
            "purpose": "mpirun 딥러닝", "eta": "18:00", "source": "mpirun",
        })
        assert r.status_code == 200
        assert r.json()["source"] == "mpirun"

        # POST wiki post
        r = client.post("/api/wiki/posts", json={
            "title": "t", "author": "a", "body": "b",
        })
        assert r.status_code == 200

        # POST chat message + 증분 폴링
        r = client.post("/api/chat/messages", json={"sender": "s", "body": "hi"})
        assert r.status_code == 200
        mid = r.json()["id"]
        r2 = client.get(f"/api/chat/messages?after={mid - 1}")
        assert r2.status_code == 200
        assert any(m["id"] == mid for m in r2.json())
