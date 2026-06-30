"""채팅 차별화 기능 검증 (팀원1) — T7 초기 50건 · 메시지 검색 · 점유 선언 보드."""
from starlette.testclient import TestClient

import main


def test_initial_load_limited_to_50():
    with TestClient(main.app) as client:
        # 60건 전송 후 초기 로드(after 없음)는 최근 50건만, 마지막이 최신
        for i in range(60):
            client.post("/api/chat/messages", json={"sender": "t", "body": f"메시지{i}"})
        rows = client.get("/api/chat/messages").json()
        assert len(rows) <= 50
        assert rows[-1]["body"] == "메시지59"
        # 시간순(오름차순) 보장
        ids = [m["id"] for m in rows]
        assert ids == sorted(ids)


def test_message_search():
    with TestClient(main.app) as client:
        client.post("/api/chat/messages", json={"sender": "kim", "body": "GPU 점유 관련 공지"})
        rows = client.get("/api/chat/messages?q=점유").json()
        assert any("점유" in m["body"] for m in rows)


def test_reservation_board():
    with TestClient(main.app) as client:
        # 빈 node/who 거절
        assert client.post("/api/chat/reservations",
                           json={"node": "", "who": ""}).json().get("error")
        rid = client.post("/api/chat/reservations", json={
            "node": "node06", "who": "kim", "until": "~20:00", "purpose": "학습",
        }).json()["id"]
        active = client.get("/api/chat/reservations").json()
        assert any(r["id"] == rid and r["node"] == "node06" for r in active)
        # 해제하면 목록에서 사라진다
        client.post(f"/api/chat/reservations/{rid}/release")
        after = client.get("/api/chat/reservations").json()
        assert all(r["id"] != rid for r in after)
