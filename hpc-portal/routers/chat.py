"""채팅 라우터 (팀원1 소유) — /api/chat/*.

  GET  /api/chat/messages?after=id   증분 폴링 (id > after)
  POST /api/chat/messages            {sender, body}

결정 T7: after 가 없는 초기 로드는 최근 50건만 (무한 증가 방지).
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from db import db_dep

router = APIRouter(prefix="/api/chat", tags=["chat"])

_INITIAL_LIMIT = 50


class MessageIn(BaseModel):
    sender: str
    body: str


@router.get("/messages")
def get_messages(after: Optional[int] = None, db=Depends(db_dep)):
    """after 가 있으면 그 id 초과 행만(증분), 없으면 최근 50건을 시간순 반환."""
    if after is not None:
        rows = db.execute(
            "SELECT id, sender, body, created_at FROM messages "
            "WHERE id > ? ORDER BY id ASC",
            (after,),
        ).fetchall()
        return [dict(r) for r in rows]
    # 초기 로드: 최근 50건을 id DESC 로 뽑고 다시 ASC 로 정렬해 반환 (T7)
    rows = db.execute(
        "SELECT id, sender, body, created_at FROM messages "
        "ORDER BY id DESC LIMIT ?",
        (_INITIAL_LIMIT,),
    ).fetchall()
    return [dict(r) for r in reversed(rows)]


@router.post("/messages")
def post_message(payload: MessageIn, db=Depends(db_dep)):
    """메시지 전송. 서버가 created_at(ISO) 생성."""
    created_at = datetime.now().isoformat()
    cur = db.execute(
        "INSERT INTO messages (sender, body, created_at) VALUES (?,?,?)",
        (payload.sender, payload.body, created_at),
    )
    db.commit()
    return {
        "id": cur.lastrowid,
        "sender": payload.sender,
        "body": payload.body,
        "created_at": created_at,
    }
