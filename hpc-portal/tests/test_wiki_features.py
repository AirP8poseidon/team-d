"""위키 차별화 기능 검증 (팀원1) — 태그·도움됨·댓글·검색.

통합 스키마(posts: tags/helpful 가산, comments 가산)를 라우터가 멱등 보장하는지 확인.
"""
from starlette.testclient import TestClient

import main


def test_create_post_with_tags_and_search():
    with TestClient(main.app) as client:
        r = client.post("/api/wiki/posts", json={
            "title": "NCCL 타임아웃 해결", "author": "kim",
            "body": "NCCL_SOCKET_IFNAME 지정", "tags": "NCCL,분산학습",
        })
        assert r.status_code == 200
        body = r.json()
        assert body["tags"] == ["NCCL", "분산학습"]
        assert body["helpful"] == 0

        # 본문 키워드 검색
        rows = client.get("/api/wiki/posts?q=NCCL").json()
        assert any("NCCL" in p["title"] for p in rows)

        # 태그 필터(정확 매칭)
        tagged = client.get("/api/wiki/posts?tag=분산학습").json()
        assert tagged and all("분산학습" in p["tags"] for p in tagged)


def test_helpful_increment_and_sort():
    with TestClient(main.app) as client:
        pid = client.post("/api/wiki/posts", json={
            "title": "도움됨 정렬용", "author": "kim", "body": "x", "tags": "정렬",
        }).json()["id"]
        # 두 번 누르면 helpful=2
        client.post(f"/api/wiki/posts/{pid}/helpful")
        res = client.post(f"/api/wiki/posts/{pid}/helpful").json()
        assert res["helpful"] == 2
        # sort=helpful 이면 최상단에 온다
        top = client.get("/api/wiki/posts?sort=helpful").json()[0]
        assert top["id"] == pid


def test_comments_crud():
    with TestClient(main.app) as client:
        pid = client.post("/api/wiki/posts", json={
            "title": "댓글 대상", "author": "kim", "body": "x",
        }).json()["id"]
        # 빈 본문 거절
        assert client.post(f"/api/wiki/posts/{pid}/comments",
                           json={"author": "a", "body": "  "}).json().get("error")
        # 정상 작성 후 목록 반영
        client.post(f"/api/wiki/posts/{pid}/comments",
                    json={"author": "lee", "body": "좋은 팁 감사합니다"})
        rows = client.get(f"/api/wiki/posts/{pid}/comments").json()
        assert any(c["body"] == "좋은 팁 감사합니다" for c in rows)
