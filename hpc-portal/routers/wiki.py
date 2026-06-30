"""위키 라우터 (팀원1 소유) — /api/wiki/*.

통합판: 연결은 중앙 db.py 의 db_dep 의존성으로 받는다(결정 1A).
스켈레톤의 기본 시그니처(SPEC §7.2)를 유지하면서 차별화 기능을 가산(additive):
  GET  /api/wiki/servers
  GET  /api/wiki/posts?q=&tag=&sort=helpful   목록(검색/태그필터/정렬)
  GET  /api/wiki/posts/{pid}                  단일 글 상세
  POST /api/wiki/posts   {title, author, body, tags}
  POST /api/wiki/posts/{pid}/helpful          도움됐어요 +1
  GET  /api/wiki/posts/{pid}/comments
  POST /api/wiki/posts/{pid}/comments  {author, body}

확장 컬럼(posts.tags, posts.helpful)과 comments 테이블은 중앙 스키마를 건드리지 않고
첫 요청 때 1회 멱등 가산(결정 2A 정신) — db.py 소유 영역은 그대로 둔다.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from db import db_dep

router = APIRouter(prefix="/api/wiki", tags=["wiki"])

_extras_ready = False


def _ensure_extras(db) -> None:
    """posts 확장 컬럼(tags/helpful) + comments 테이블을 멱등 가산. 1회만 수행."""
    global _extras_ready
    if _extras_ready:
        return
    cols = {r[1] for r in db.execute("PRAGMA table_info(posts)").fetchall()}
    if "tags" not in cols:
        db.execute("ALTER TABLE posts ADD COLUMN tags TEXT DEFAULT ''")
    if "helpful" not in cols:
        db.execute("ALTER TABLE posts ADD COLUMN helpful INTEGER DEFAULT 0")
    db.execute(
        "CREATE TABLE IF NOT EXISTS comments("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "post_id INTEGER, author TEXT, body TEXT, created_at TEXT)"
    )
    # ── 데모 시드(통합본에서도 태그칩·도움순·댓글이 바로 보이도록) ──────────────
    # 중앙 시드 글(1·2·3)에 태그/도움수를 '비어있을 때만' 1회 부여(멱등).
    for pid, tg, hp in (
        (1, "SLURM,sbatch,입문", 1),
        (2, "MPI,분산학습", 1),
        (3, "스토리지,NFS,트러블슈팅", 1),
    ):
        db.execute(
            "UPDATE posts SET tags=?, helpful=? "
            "WHERE id=? AND (tags IS NULL OR tags='') AND COALESCE(helpful,0)=0",
            (tg, hp, pid),
        )
    # 차별화 기능(태그/필터/도움순/점유보드 연계)을 한눈에 보여줄 노하우 글 — 제목 중복 없을 때만 추가(멱등).
    demo_posts = [
        ("GPU 메모리 부족(OOM) 빠른 진단", "김연구",
         "nvidia-smi 로 점유 확인 → batch_size/precision 조정. torch.cuda.empty_cache() 도 체크.",
         "GPU,트러블슈팅,PyTorch", 1),
        ("분산학습 NCCL 타임아웃 잡기", "박엔지니어",
         "NCCL_SOCKET_IFNAME 으로 인터페이스 고정, NCCL_DEBUG=INFO 로 로그 확인.",
         "NCCL,분산학습,GPU", 1),
        ("Conda 환경 공유 베스트프랙티스", "이수민",
         "environment.yml 로 고정 후 conda env export --no-builds 로 OS 차이 흡수.",
         "환경설정,Conda", 0),
        ("대용량 데이터셋은 /scratch 로", "김연구",
         "홈 대신 /scratch 에 두고 학습. 끝나면 정리하기(쿼터 공유).",
         "스토리지,데이터", 1),
        ("sbatch 배열 작업(job array) 예제", "박엔지니어",
         "#SBATCH --array=0-9 로 하이퍼파라미터 스윕을 한 번에. $SLURM_ARRAY_TASK_ID 활용.",
         "SLURM,sbatch", 0),
        ("노드 점유 에티켓 — 채팅 점유보드 쓰는 법", "이수민",
         "장시간 점유 전 채팅 위젯의 '점유 선언 보드'에 노드/예상시간/용도를 남기면 충돌이 줄어요.",
         "운영,점유", 1),
    ]
    for title, author, body, tags, hp in demo_posts:
        db.execute(
            "INSERT INTO posts(title,author,body,created_at,tags,helpful) "
            "SELECT ?,?,?,?,?,? WHERE NOT EXISTS (SELECT 1 FROM posts WHERE title=?)",
            (title, author, body, "2026-06-30T08:00:00", tags, hp, title),
        )
    # 댓글: 중앙 글(1·3) + 데모 글 일부에 비었을 때만 1회 부착
    if db.execute("SELECT COUNT(*) FROM comments").fetchone()[0] == 0:
        seed = [
            (1, "lee", "sbatch 쓸 때 --gres=gpu:1 빼먹어서 CPU로 돌던 적 있어요. 꼭 확인!", "2026-06-30T09:30:00"),
            (1, "park", "run.sh 안에 module load 까먹지 마세요. 환경 안 잡혀서 한참 헤맸네요.", "2026-06-30T10:05:00"),
            (3, "kim", "mount -a 전에 dmesg 로 NFS 타임아웃 로그부터 보면 원인 빨라요.", "2026-06-30T11:20:00"),
        ]
        db.executemany(
            "INSERT INTO comments(post_id,author,body,created_at) VALUES(?,?,?,?)", seed
        )
        for title, a, b in (
            ("GPU 메모리 부족(OOM) 빠른 진단", "정연구", "gradient checkpointing 도 메모리 많이 아껴요!"),
            ("노드 점유 에티켓 — 채팅 점유보드 쓰는 법", "한엔지니어", "보드 덕분에 node07 겹침이 확 줄었어요."),
        ):
            row = db.execute("SELECT id FROM posts WHERE title=?", (title,)).fetchone()
            if row:
                db.execute(
                    "INSERT INTO comments(post_id,author,body,created_at) VALUES(?,?,?,?)",
                    (row[0], a, b, "2026-06-30T12:00:00"),
                )
    db.commit()
    _extras_ready = True


def _split_tags(s):
    return [t.strip() for t in (s or "").split(",") if t.strip()]


def _tags_to_str(tags):
    if isinstance(tags, (list, tuple)):
        parts = [str(t).strip() for t in tags if str(t).strip()]
    else:
        parts = _split_tags(tags)
    return ",".join(parts)


def _row_to_post(r):
    d = dict(r)
    d["tags"] = _split_tags(d.get("tags"))
    d["helpful"] = int(d.get("helpful") or 0)
    return d


class PostIn(BaseModel):
    title: str
    author: str = "익명"
    body: str = ""
    tags: object = ""   # 문자열("a,b") 또는 배열(["a","b"]) 모두 허용


class CommentIn(BaseModel):
    author: str = "익명"
    body: str = ""


@router.get("/servers")
def get_servers(db=Depends(db_dep)):
    """서버 환경 카드 목록 (SPEC §7.2 그대로 — modules는 콤마 문자열)."""
    rows = db.execute(
        "SELECT id, name, os, spec, modules, ssh FROM servers ORDER BY id"
    ).fetchall()
    return [dict(r) for r in rows]


@router.get("/posts")
def get_posts(
    q: Optional[str] = None,
    tag: Optional[str] = None,
    sort: Optional[str] = None,
    db=Depends(db_dep),
):
    """노하우 게시판 목록. q(제목·본문 검색) / tag(태그 필터) / sort=helpful(도움순)."""
    _ensure_extras(db)
    where, params = [], []
    if q:
        like = f"%{q}%"
        where.append("(title LIKE ? OR body LIKE ?)")
        params += [like, like]
    if tag:
        where.append("(',' || COALESCE(tags,'') || ',') LIKE ?")
        params.append(f"%,{tag},%")
    clause = (" WHERE " + " AND ".join(where)) if where else ""
    order = ("ORDER BY helpful DESC, created_at DESC, id DESC"
             if sort == "helpful" else "ORDER BY created_at DESC, id DESC")
    rows = db.execute(
        "SELECT id,title,author,body,created_at,tags,helpful FROM posts" + clause + " " + order,
        params,
    ).fetchall()
    return [_row_to_post(r) for r in rows]


@router.get("/posts/{pid}")
def get_post(pid: int, db=Depends(db_dep)):
    """단일 글 상세(tags 배열, helpful 포함)."""
    _ensure_extras(db)
    r = db.execute(
        "SELECT id,title,author,body,created_at,tags,helpful FROM posts WHERE id=?", (pid,)
    ).fetchone()
    if not r:
        return {"error": "not found"}
    return _row_to_post(r)


@router.post("/posts")
def create_post(payload: PostIn, db=Depends(db_dep)):
    """노하우 글 작성 → 저장 후 생성된 글 반환."""
    _ensure_extras(db)
    now = datetime.now().isoformat(timespec="seconds")
    title = (payload.title or "").strip() or "(제목 없음)"
    author = (payload.author or "").strip() or "익명"
    body = (payload.body or "").strip() or "(요약 없음)"
    tags = _tags_to_str(payload.tags)
    cur = db.execute(
        "INSERT INTO posts(title,author,body,created_at,tags,helpful) VALUES(?,?,?,?,?,0)",
        (title, author, body, now, tags),
    )
    db.commit()
    return {"id": cur.lastrowid, "title": title, "author": author, "body": body,
            "created_at": now, "tags": _split_tags(tags), "helpful": 0}


@router.post("/posts/{pid}/helpful")
def mark_helpful(pid: int, db=Depends(db_dep)):
    """도움됐어요 +1 → {id, helpful 새값}."""
    _ensure_extras(db)
    cur = db.execute("UPDATE posts SET helpful = COALESCE(helpful,0) + 1 WHERE id=?", (pid,))
    db.commit()
    if cur.rowcount == 0:
        return {"error": "not found"}
    val = db.execute("SELECT helpful FROM posts WHERE id=?", (pid,)).fetchone()[0]
    return {"id": pid, "helpful": int(val)}


@router.get("/posts/{pid}/comments")
def list_comments(pid: int, db=Depends(db_dep)):
    """게시글 댓글 목록(시간순)."""
    _ensure_extras(db)
    rows = db.execute(
        "SELECT id,post_id,author,body,created_at FROM comments WHERE post_id=? "
        "ORDER BY created_at ASC, id ASC", (pid,)
    ).fetchall()
    return [dict(r) for r in rows]


@router.post("/posts/{pid}/comments")
def create_comment(pid: int, payload: CommentIn, db=Depends(db_dep)):
    """댓글 작성 → 저장 후 생성 객체 반환. 빈 body 거절."""
    _ensure_extras(db)
    body = (payload.body or "").strip()
    if not body:
        return {"error": "empty body"}
    author = (payload.author or "").strip() or "익명"
    now = datetime.now().isoformat(timespec="seconds")
    cur = db.execute(
        "INSERT INTO comments(post_id,author,body,created_at) VALUES(?,?,?,?)",
        (pid, author, body, now),
    )
    db.commit()
    return {"id": cur.lastrowid, "post_id": pid, "author": author, "body": body, "created_at": now}
