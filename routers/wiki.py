"""
정보공유(위키) 라우터 — 팀원1 소유
/api/wiki/*  : 서버 환경 목록 · 노하우 게시판(검색/작성)

설계 메모(통합 안전):
- DB는 환경변수 HPC_DB(기본 'hpc.db')의 SQLite 파일을 공유한다.
- 본 라우터는 자기 테이블(servers, posts)을 CREATE TABLE IF NOT EXISTS 로 보장하고
  비어 있으면 1회 시드한다 → 팀장 db.py 유무와 무관하게 /docs 단독 응답 가능(통합 전제 충족).
- 통합 시 팀장은 main.py 에서 `from routers import wiki; app.include_router(wiki.router)` 한 줄만.
"""
import os
import sqlite3
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel

DB_PATH = os.environ.get("HPC_DB", "hpc.db")

router = APIRouter(prefix="/api/wiki", tags=["wiki"])


def _conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


# --- 시드 데이터 (서버 3대) — DEV_BLUEPRINT/프로토타입 기준 ---
_SEED_SERVERS = [
    {
        "name": "gpu-cluster", "os": "Ubuntu 22.04 LTS",
        "spec": "AMD EPYC 7763 64코어 x2 · NVIDIA A100 80GB x4 · 512GB DDR4 · NVMe 3.2TB(scratch)",
        "modules": "python 3.10,CUDA 12.2,cuDNN 8.9,conda 23.7,OpenMPI 4.1,NCCL 2.18,PyTorch 2.2",
        "ssh": "ssh 사번@gpu-cluster.hpc.corp.local",
    },
    {
        "name": "cpu-cluster", "os": "Rocky Linux 8.9",
        "spec": "Intel Xeon Platinum 8480+ 56코어 x2 · GPU 없음 · 256GB DDR5 · Lustre /scratch 1.5PB",
        "modules": "python 3.11,conda 23.7,OpenMPI 4.1,Intel MKL,GCC 11,Slurm 23.02",
        "ssh": "ssh 사번@cpu-cluster.hpc.corp.local",
    },
    {
        "name": "fat-node", "os": "Ubuntu 22.04 LTS",
        "spec": "AMD EPYC 9654 96코어 x2 · NVIDIA L40S 48GB x2 · 4TB DDR5 · NVMe 15TB(로컬)",
        "modules": "python 3.10,CUDA 12.2,conda 23.7,R 4.3,Spark 3.5,OpenMPI 4.1",
        "ssh": "ssh 사번@fat-node.hpc.corp.local",
    },
]

# --- 시드 데이터 (노하우 게시판) ---  (title,author,body,created_at,tags)
_SEED_POSTS = [
    ("A100에서 PyTorch OOM 줄이는 법", "김연구",
     "gradient checkpointing + AMP(mixed precision) 조합으로 메모리 30% 절약한 실전 설정 정리.", "2026-06-18T09:12:00",
     "OOM,PyTorch,GPU"),
    ("conda 환경 빠르게 복제하기", "박엔지니어",
     "environment.yml export & --clone 비교, 그리고 mamba로 설치 속도 5배 올린 팁.", "2026-06-15T14:30:00",
     "conda,환경"),
    ("Slurm 작업이 PENDING에서 안 풀릴 때 체크리스트", "이운영",
     "파티션 자원 부족 / QOS 한도 / 잘못된 gres 요청 등 PENDING 원인 6가지 진단법.", "2026-06-12T10:05:00",
     "Slurm,스케줄러"),
    ("Lustre /scratch 빠르게 쓰는 I/O 패턴", "최데이터",
     "작은 파일 수십만 개 대신 tar로 묶어 읽기, stripe count 조절로 처리량 개선.", "2026-06-09T16:40:00",
     "Lustre,스토리지,IO"),
    ("멀티노드 분산학습 NCCL 타임아웃 해결", "김연구",
     "NCCL_SOCKET_IFNAME, NCCL_DEBUG 설정과 인피니밴드 인터페이스 지정으로 행(hang) 제거.", "2026-06-05T11:20:00",
     "NCCL,분산학습,GPU"),
    ("fat-node에서 4TB 메모리 인메모리 전처리 팁", "정분석",
     "pandas 대신 polars로 lazy 처리, 메모리 모니터링은 htop+nvidia-smi 동시 활용.", "2026-06-02T13:55:00",
     "전처리,메모리"),
    ("sbatch 로그를 작업별로 깔끔하게 모으기", "박엔지니어",
     "--output=logs/%x-%j.out 패턴과 회전(rotation) 스크립트로 로그 폭주 방지.", "2026-05-28T09:48:00",
     "Slurm,로그"),
    ("VS Code Remote-SSH로 클러스터 개발환경 세팅", "이운영",
     "로그인 노드 부하 줄이려고 srun으로 잡은 노드에 직접 붙는 설정 가이드.", "2026-05-24T15:10:00",
     "VSCode,SSH,환경"),
]

# --- 시드 데이터 (댓글) — post_id 1,3 에 부착 ---
_SEED_COMMENTS = [
    (1, "박엔지니어", "AMP 적용했더니 batch size 2배까지 올라가네요. 감사합니다!", "2026-06-18T10:30:00"),
    (1, "정분석", "gradient checkpointing은 속도 손해가 좀 있던데 체감 어느 정도였나요?", "2026-06-18T13:05:00"),
    (3, "최데이터", "gres 오타 때문에 한참 헤맸는데 딱 이 글 덕분에 해결했습니다.", "2026-06-12T15:20:00"),
]


def init_db():
    """테이블 보장 + (비어 있으면) 시드. 멱등(idempotent)."""
    con = _conn()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS servers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, os TEXT, spec TEXT, modules TEXT, ssh TEXT
        )""")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS posts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, author TEXT, body TEXT, created_at TEXT
        )""")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS comments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER, author TEXT, body TEXT, created_at TEXT
        )""")

    # --- 안전 마이그레이션: 기존 DB에 posts 컬럼 추가 (SQLite는 ADD COLUMN IF NOT EXISTS 미지원) ---
    post_cols = {r[1] for r in cur.execute("PRAGMA table_info(posts)").fetchall()}
    if "tags" not in post_cols:
        cur.execute("ALTER TABLE posts ADD COLUMN tags TEXT DEFAULT ''")
    if "helpful" not in post_cols:
        cur.execute("ALTER TABLE posts ADD COLUMN helpful INTEGER DEFAULT 0")

    if cur.execute("SELECT COUNT(*) FROM servers").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO servers(name,os,spec,modules,ssh) VALUES(:name,:os,:spec,:modules,:ssh)",
            _SEED_SERVERS,
        )
    if cur.execute("SELECT COUNT(*) FROM posts").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO posts(title,author,body,created_at,tags) VALUES(?,?,?,?,?)",
            _SEED_POSTS,
        )
    if cur.execute("SELECT COUNT(*) FROM comments").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO comments(post_id,author,body,created_at) VALUES(?,?,?,?)",
            _SEED_COMMENTS,
        )
    con.commit()
    con.close()


def _split_tags(s):
    """콤마 문자열 → 정리된 태그 배열."""
    return [t.strip() for t in (s or "").split(",") if t.strip()]


def _row_to_post(r):
    """posts row(dict 변환 가능) → tags 배열 + helpful 정수 포함 dict."""
    d = dict(r)
    d["tags"] = _split_tags(d.get("tags"))
    d["helpful"] = int(d.get("helpful") or 0)
    return d


# --- 요청 모델 ---
class PostIn(BaseModel):
    title: str
    author: str = "익명"
    body: str = ""
    tags: object = ""   # 문자열("a,b") 또는 배열(["a","b"]) 모두 허용


class CommentIn(BaseModel):
    author: str = "익명"
    body: str = ""


def _tags_to_str(tags):
    """입력 tags(문자열 또는 배열) → 정규화된 콤마 문자열."""
    if isinstance(tags, (list, tuple)):
        parts = [str(t).strip() for t in tags if str(t).strip()]
    else:
        parts = _split_tags(tags)
    return ",".join(parts)


# --- 엔드포인트 ---
@router.get("/servers")
def list_servers():
    """서버 환경 목록. modules는 콤마 문자열을 배열로 변환해 반환."""
    con = _conn()
    rows = con.execute("SELECT id,name,os,spec,modules,ssh FROM servers ORDER BY id").fetchall()
    con.close()
    out = []
    for r in rows:
        d = dict(r)
        d["modules"] = [m for m in (d.get("modules") or "").split(",") if m]
        out.append(d)
    return out


@router.get("/posts")
def list_posts(q: str = "", tag: str = "", sort: str = ""):
    """노하우 게시판 목록.
    - q: 제목·본문 부분 검색
    - tag: 특정 태그 보유 글만 (q와 병행 시 AND)
    - sort=helpful: 도움됨 내림차순(동률은 최신순), 기본은 최신순.
    """
    where, params = [], []
    if q:
        like = f"%{q}%"
        where.append("(title LIKE ? OR body LIKE ?)")
        params += [like, like]
    if tag:
        # 콤마 구분 문자열 내 정확 매칭(부분 태그 오매칭 방지)
        where.append("(',' || tags || ',') LIKE ?")
        params.append(f"%,{tag},%")
    clause = (" WHERE " + " AND ".join(where)) if where else ""
    order = ("ORDER BY helpful DESC, created_at DESC, id DESC"
             if sort == "helpful" else "ORDER BY created_at DESC, id DESC")
    con = _conn()
    rows = con.execute(
        "SELECT id,title,author,body,created_at,tags,helpful FROM posts" + clause + " " + order,
        params,
    ).fetchall()
    con.close()
    return [_row_to_post(r) for r in rows]


@router.get("/posts/{pid}")
def get_post(pid: int):
    """단일 글 상세(tags 배열, helpful 포함). 없으면 error."""
    con = _conn()
    r = con.execute(
        "SELECT id,title,author,body,created_at,tags,helpful FROM posts WHERE id=?", (pid,)
    ).fetchone()
    con.close()
    if not r:
        return {"error": "not found"}
    return _row_to_post(r)


@router.post("/posts")
def create_post(p: PostIn):
    """노하우 글 작성 → 저장 후 생성된 글 반환."""
    now = datetime.now().isoformat(timespec="seconds")
    title = (p.title or "").strip() or "(제목 없음)"
    author = (p.author or "").strip() or "익명"
    body = (p.body or "").strip() or "(요약 없음)"
    tags = _tags_to_str(p.tags)
    con = _conn()
    cur = con.execute(
        "INSERT INTO posts(title,author,body,created_at,tags,helpful) VALUES(?,?,?,?,?,0)",
        (title, author, body, now, tags),
    )
    con.commit()
    pid = cur.lastrowid
    con.close()
    return {"id": pid, "title": title, "author": author, "body": body,
            "created_at": now, "tags": _split_tags(tags), "helpful": 0}


@router.post("/posts/{pid}/helpful")
def mark_helpful(pid: int):
    """도움됐어요 +1 → {id, helpful 새값} 반환."""
    con = _conn()
    cur = con.execute("UPDATE posts SET helpful = COALESCE(helpful,0) + 1 WHERE id=?", (pid,))
    con.commit()
    if cur.rowcount == 0:
        con.close()
        return {"error": "not found"}
    val = con.execute("SELECT helpful FROM posts WHERE id=?", (pid,)).fetchone()[0]
    con.close()
    return {"id": pid, "helpful": int(val)}


@router.get("/posts/{pid}/comments")
def list_comments(pid: int):
    """게시글 댓글 목록(시간순)."""
    con = _conn()
    rows = con.execute(
        "SELECT id,post_id,author,body,created_at FROM comments WHERE post_id=? "
        "ORDER BY created_at ASC, id ASC", (pid,)
    ).fetchall()
    con.close()
    return [dict(r) for r in rows]


@router.post("/posts/{pid}/comments")
def create_comment(pid: int, c: CommentIn):
    """댓글 작성 → 저장 후 생성 객체 반환. 빈 body 거절."""
    body = (c.body or "").strip()
    if not body:
        return {"error": "empty body"}
    author = (c.author or "").strip() or "익명"
    now = datetime.now().isoformat(timespec="seconds")
    con = _conn()
    cur = con.execute(
        "INSERT INTO comments(post_id,author,body,created_at) VALUES(?,?,?,?)",
        (pid, author, body, now),
    )
    con.commit()
    cid = cur.lastrowid
    con.close()
    return {"id": cid, "post_id": pid, "author": author, "body": body, "created_at": now}


# 임포트 시 1회 보장(단독 실행/통합 모두 안전 — IF NOT EXISTS 멱등)
init_db()
