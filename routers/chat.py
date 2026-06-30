"""
실시간 채팅 라우터 — 팀원1 소유
/api/chat/*  : 메시지 폴링(GET after=id) · 전송(POST)

설계 메모:
- WebSocket 미사용, 2~3초 폴링(채팅 위젯이 GET ?after=<마지막id>로 신규만 가져감).
- DB는 환경변수 HPC_DB(기본 'hpc.db') SQLite 공유. messages 테이블 자체 보장 + 1회 시드.
- 통합: 팀장 main.py 에서 `from routers import chat; app.include_router(chat.router)` 한 줄.
"""
import os
import sqlite3
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel

DB_PATH = os.environ.get("HPC_DB", "hpc.db")

router = APIRouter(prefix="/api/chat", tags=["chat"])


def _conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


_SEED_MESSAGES = [
    ("시스템", "HPC 포털 채팅에 오신 걸 환영합니다. 노드 사용 계획을 여기서 공유해 주세요.", "2026-06-30T09:00:00"),
    ("이운영", "오늘 오전 node02 정기 점검 있습니다. 작업 제출 잠시 보류 부탁드려요.", "2026-06-30T09:05:00"),
]

# 노드 점유 "선언"(계획/의도) 시드 — SLURM 실측이 아니라 사람 맥락.
_SEED_RESERVATIONS = [
    ("node04", "김연구", "~18:00", "ResNet 학습", "2026-06-30T09:10:00"),
    ("node07", "박엔지니어", "~12:00", "데이터 전처리", "2026-06-30T09:12:00"),
]


def init_db():
    """messages 테이블 보장 + (비어 있으면) 시드. 멱등."""
    con = _conn()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT, body TEXT, created_at TEXT
        )""")
    if cur.execute("SELECT COUNT(*) FROM messages").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO messages(sender,body,created_at) VALUES(?,?,?)",
            _SEED_MESSAGES,
        )
    # 노드 점유 선언 보드 — 멱등 생성 + 비었을 때만 시드.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reservations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node TEXT, who TEXT, until TEXT, purpose TEXT,
            created_at TEXT, released INTEGER DEFAULT 0
        )""")
    if cur.execute("SELECT COUNT(*) FROM reservations").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO reservations(node,who,until,purpose,created_at) VALUES(?,?,?,?,?)",
            _SEED_RESERVATIONS,
        )
    con.commit()
    con.close()


class MessageIn(BaseModel):
    sender: str = "익명"
    body: str


class ReservationIn(BaseModel):
    node: str = ""
    who: str = ""
    until: str = ""
    purpose: str = ""


@router.get("/messages")
def list_messages(after: int = 0, q: str = ""):
    """q가 있으면 body/sender LIKE 부분검색(시간순). q 없으면 기존 after 동작 유지."""
    con = _conn()
    q = (q or "").strip()
    if q:
        like = "%" + q + "%"
        rows = con.execute(
            "SELECT id,sender,body,created_at FROM messages "
            "WHERE body LIKE ? OR sender LIKE ? ORDER BY id",
            (like, like),
        ).fetchall()
    else:
        rows = con.execute(
            "SELECT id,sender,body,created_at FROM messages WHERE id > ? ORDER BY id",
            (after,),
        ).fetchall()
    con.close()
    return [dict(r) for r in rows]


@router.get("/reservations")
def list_reservations():
    """활성(released=0) 점유 선언만 created_at, id 순."""
    con = _conn()
    rows = con.execute(
        "SELECT id,node,who,until,purpose,created_at FROM reservations "
        "WHERE released = 0 ORDER BY created_at, id",
    ).fetchall()
    con.close()
    return [dict(r) for r in rows]


@router.post("/reservations")
def create_reservation(r: ReservationIn):
    """점유 선언 저장 → 생성 객체 반환. 빈 node/who는 거절."""
    node = (r.node or "").strip()
    who = (r.who or "").strip()
    if not node or not who:
        return {"error": "node and who are required"}
    until = (r.until or "").strip()
    purpose = (r.purpose or "").strip()
    now = datetime.now().isoformat(timespec="seconds")
    con = _conn()
    cur = con.execute(
        "INSERT INTO reservations(node,who,until,purpose,created_at) VALUES(?,?,?,?,?)",
        (node, who, until, purpose, now),
    )
    con.commit()
    rid = cur.lastrowid
    con.close()
    return {"id": rid, "node": node, "who": who, "until": until,
            "purpose": purpose, "created_at": now, "released": 0}


@router.post("/reservations/{rid}/release")
def release_reservation(rid: int):
    """해당 선언을 해제(released=1)."""
    con = _conn()
    con.execute("UPDATE reservations SET released = 1 WHERE id = ?", (rid,))
    con.commit()
    con.close()
    return {"ok": True}


@router.post("/messages")
def create_message(m: MessageIn):
    """메시지 전송 → 저장 후 생성된 메시지 반환."""
    body = (m.body or "").strip()
    if not body:
        return {"error": "empty body"}
    sender = (m.sender or "").strip() or "익명"
    now = datetime.now().isoformat(timespec="seconds")
    con = _conn()
    cur = con.execute(
        "INSERT INTO messages(sender,body,created_at) VALUES(?,?,?)",
        (sender, body, now),
    )
    con.commit()
    mid = cur.lastrowid
    con.close()
    return {"id": mid, "sender": sender, "body": body, "created_at": now}


init_db()
