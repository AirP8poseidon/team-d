"""채팅 라우터 (팀원1 소유) — /api/chat/*.

통합판: 연결은 중앙 db.py 의 db_dep 의존성으로 받는다(결정 1A).
  GET  /api/chat/messages?after=id   증분 폴링 (id > after)
  GET  /api/chat/messages?q=키워드    메시지 검색(가산)
  POST /api/chat/messages            {sender, body}
  GET  /api/chat/reservations         노드 점유 "선언" 보드(가산)
  POST /api/chat/reservations         {node, who, until, purpose}
  POST /api/chat/reservations/{rid}/release

결정 T7: after 가 없는 초기 로드는 최근 50건만 (무한 증가 방지).
reservations 테이블은 중앙 스키마를 건드리지 않고 첫 요청 때 1회 멱등 가산.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from db import db_dep

router = APIRouter(prefix="/api/chat", tags=["chat"])

_INITIAL_LIMIT = 50
_extras_ready = False

# 노드 점유 "선언"(계획/의도) 시드 — SLURM 실측이 아니라 사람 맥락 (node01..node08 키).
_SEED_RESERVATIONS = [
    ("node04", "김연구", "~18:00", "ResNet 학습", "2026-06-30T09:10:00"),
    ("node07", "박엔지니어", "~12:00", "데이터 전처리", "2026-06-30T09:12:00"),
]


def _ensure_extras(db) -> None:
    """reservations 테이블을 멱등 가산 + 비었을 때만 시드. 1회만 수행."""
    global _extras_ready
    if _extras_ready:
        return
    db.execute(
        "CREATE TABLE IF NOT EXISTS reservations("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "node TEXT, who TEXT, until TEXT, purpose TEXT,"
        "created_at TEXT, released INTEGER DEFAULT 0)"
    )
    if db.execute("SELECT COUNT(*) FROM reservations").fetchone()[0] == 0:
        db.executemany(
            "INSERT INTO reservations(node,who,until,purpose,created_at) VALUES(?,?,?,?,?)",
            _SEED_RESERVATIONS,
        )
    db.commit()
    _extras_ready = True


class MessageIn(BaseModel):
    sender: str = "익명"
    body: str


class ReservationIn(BaseModel):
    node: str = ""
    who: str = ""
    until: str = ""
    purpose: str = ""


@router.get("/messages")
def get_messages(after: Optional[int] = None, q: Optional[str] = None, db=Depends(db_dep)):
    """q가 있으면 body/sender 부분검색(시간순). 아니면 after 증분, 없으면 최근 50건(T7)."""
    q = (q or "").strip()
    if q:
        like = f"%{q}%"
        rows = db.execute(
            "SELECT id,sender,body,created_at FROM messages "
            "WHERE body LIKE ? OR sender LIKE ? ORDER BY id ASC",
            (like, like),
        ).fetchall()
        return [dict(r) for r in rows]
    if after is not None and after > 0:
        rows = db.execute(
            "SELECT id,sender,body,created_at FROM messages WHERE id > ? ORDER BY id ASC",
            (after,),
        ).fetchall()
        return [dict(r) for r in rows]
    # 초기 로드: 최근 50건을 id DESC 로 뽑고 시간순으로 되돌림 (T7)
    rows = db.execute(
        "SELECT id,sender,body,created_at FROM messages ORDER BY id DESC LIMIT ?",
        (_INITIAL_LIMIT,),
    ).fetchall()
    return [dict(r) for r in reversed(rows)]


@router.post("/messages")
def post_message(payload: MessageIn, db=Depends(db_dep)):
    """메시지 전송 → 저장 후 생성된 메시지 반환. 빈 body 거절."""
    body = (payload.body or "").strip()
    if not body:
        return {"error": "empty body"}
    sender = (payload.sender or "").strip() or "익명"
    now = datetime.now().isoformat(timespec="seconds")
    cur = db.execute(
        "INSERT INTO messages(sender,body,created_at) VALUES(?,?,?)",
        (sender, body, now),
    )
    db.commit()
    return {"id": cur.lastrowid, "sender": sender, "body": body, "created_at": now}


@router.get("/reservations")
def list_reservations(db=Depends(db_dep)):
    """활성(released=0) 점유 선언만 created_at, id 순."""
    _ensure_extras(db)
    rows = db.execute(
        "SELECT id,node,who,until,purpose,created_at FROM reservations "
        "WHERE released = 0 ORDER BY created_at, id"
    ).fetchall()
    return [dict(r) for r in rows]


@router.post("/reservations")
def create_reservation(payload: ReservationIn, db=Depends(db_dep)):
    """점유 선언 저장 → 생성 객체 반환. 빈 node/who는 거절."""
    _ensure_extras(db)
    node = (payload.node or "").strip()
    who = (payload.who or "").strip()
    if not node or not who:
        return {"error": "node and who are required"}
    until = (payload.until or "").strip()
    purpose = (payload.purpose or "").strip()
    now = datetime.now().isoformat(timespec="seconds")
    cur = db.execute(
        "INSERT INTO reservations(node,who,until,purpose,created_at) VALUES(?,?,?,?,?)",
        (node, who, until, purpose, now),
    )
    db.commit()
    return {"id": cur.lastrowid, "node": node, "who": who, "until": until,
            "purpose": purpose, "created_at": now, "released": 0}


@router.post("/reservations/{rid}/release")
def release_reservation(rid: int, db=Depends(db_dep)):
    """해당 선언을 해제(released=1)."""
    _ensure_extras(db)
    db.execute("UPDATE reservations SET released = 1 WHERE id = ?", (rid,))
    db.commit()
    return {"ok": True}
