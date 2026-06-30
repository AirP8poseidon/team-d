"""위키 라우터 (팀원1 소유) — /api/wiki/*.

스켈레톤 단계: 시그니처/쿼리는 SPEC §7.2 그대로, 최소 구현. 팀원1 이 UI 배선.
  GET  /api/wiki/servers
  GET  /api/wiki/posts?q=검색어
  POST /api/wiki/posts   {title, author, body}
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from db import db_dep

router = APIRouter(prefix="/api/wiki", tags=["wiki"])


class PostIn(BaseModel):
    title: str
    author: str
    body: str


@router.get("/servers")
def get_servers(db=Depends(db_dep)):
    """서버 환경 카드 목록."""
    rows = db.execute(
        "SELECT id, name, os, spec, modules, ssh FROM servers ORDER BY id"
    ).fetchall()
    return [dict(r) for r in rows]


@router.get("/posts")
def get_posts(q: Optional[str] = None, db=Depends(db_dep)):
    """노하우 게시판. q 가 있으면 제목/본문 키워드 검색."""
    if q:
        like = f"%{q}%"
        rows = db.execute(
            "SELECT id, title, author, body, created_at FROM posts "
            "WHERE title LIKE ? OR body LIKE ? ORDER BY id DESC",
            (like, like),
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT id, title, author, body, created_at FROM posts ORDER BY id DESC"
        ).fetchall()
    return [dict(r) for r in rows]


@router.post("/posts")
def post_post(payload: PostIn, db=Depends(db_dep)):
    """게시글 작성. 서버가 created_at(ISO) 생성."""
    created_at = datetime.now().isoformat()
    cur = db.execute(
        "INSERT INTO posts (title, author, body, created_at) VALUES (?,?,?,?)",
        (payload.title, payload.author, payload.body, created_at),
    )
    db.commit()
    return {
        "id": cur.lastrowid,
        "title": payload.title,
        "author": payload.author,
        "body": payload.body,
        "created_at": created_at,
    }
