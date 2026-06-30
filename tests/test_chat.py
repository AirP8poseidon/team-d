"""채팅 라우터 최소 검증 — 스모크 + T7(초기 로드 최근 50개) + 멱등 시드."""


def test_messages_smoke(client):
    r = client.get("/api/chat/messages")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_reservations_smoke(client):
    r = client.get("/api/chat/reservations")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_post_and_poll(client):
    before = client.get("/api/chat/messages").json()
    last_id = before[-1]["id"] if before else 0
    client.post("/api/chat/messages", json={"sender": "테스터", "body": "안녕하세요 폴링 테스트"})
    new = client.get(f"/api/chat/messages?after={last_id}").json()
    assert any(m["body"] == "안녕하세요 폴링 테스트" for m in new)


def test_initial_load_limit_50(client):
    """T7: 초기 로드(after 없음)는 최근 50개까지만 반환."""
    for i in range(60):
        client.post("/api/chat/messages", json={"sender": "봇", "body": f"메시지{i}"})
    rows = client.get("/api/chat/messages").json()
    assert len(rows) <= 50
    # 최신순 보장: 마지막 항목이 가장 최근에 넣은 메시지 계열
    assert rows[-1]["body"] == "메시지59"


def test_search(client):
    client.post("/api/chat/messages", json={"sender": "검색대상", "body": "GPU 할당 문의"})
    rows = client.get("/api/chat/messages?q=GPU").json()
    assert any("GPU" in m["body"] for m in rows)


def test_idempotent_seed(client):
    """init_db()를 다시 불러도 시드가 중복되지 않는다(멱등)."""
    from routers import chat
    n1 = len(client.get("/api/chat/reservations").json())
    chat.init_db()
    n2 = len(client.get("/api/chat/reservations").json())
    assert n1 == n2
