"""위키 라우터 최소 검증 — 스모크 + 게시글 작성/검색 + 멱등 시드."""


def test_servers_smoke(client):
    r = client.get("/api/wiki/servers")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list) and len(body) >= 1


def test_posts_smoke(client):
    r = client.get("/api/wiki/posts")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_create_and_search_post(client):
    client.post(
        "/api/wiki/posts",
        json={"title": "CUDA 버전 충돌 해결", "body": "module load cuda/12.2 로 고정", "author": "테스터"},
    )
    rows = client.get("/api/wiki/posts?q=CUDA").json()
    assert any("CUDA" in p["title"] for p in rows)


def test_idempotent_seed(client):
    """init_db()를 다시 불러도 서버 시드가 중복되지 않는다(멱등)."""
    from routers import wiki
    n1 = len(client.get("/api/wiki/servers").json())
    wiki.init_db()
    n2 = len(client.get("/api/wiki/servers").json())
    assert n1 == n2
