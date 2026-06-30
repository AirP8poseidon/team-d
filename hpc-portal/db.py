"""SQLite 연결 · 테이블 초기화 · 시드 (팀장 소유).

엔지니어링 잠금 결정 반영:
- 1A: 요청별 connection + check_same_thread=False + WAL + busy_timeout.
- 2A: 멱등 초기화 — CREATE TABLE IF NOT EXISTS + "비었을 때만" 시드.
- T8: 노드 키 상수 NODES = node01..node08 (전 테이블 통합 키).
"""
from __future__ import annotations

import os
import sqlite3
from datetime import datetime

# ── T8: 통합 키 — 모든 node-keyed 테이블/파일이 이 집합을 공유한다 ────────────
# 실클러스터는 HPC_NODES 환경변수로 실제 노드명을 주입한다.
#   예) export HPC_NODES="master,node1,node2,...,node13"
# 미설정 시 데모/mock 기본값(node01..node08) — 샘플·테스트가 이 집합을 쓴다.
_DEFAULT_NODES = [f"node{i:02d}" for i in range(1, 9)]  # node01 .. node08
NODES = [n.strip() for n in os.environ.get("HPC_NODES", "").split(",") if n.strip()] or _DEFAULT_NODES

# DB 경로. 테스트는 환경변수 HPC_DB_PATH 로 임시 DB를 가리킬 수 있다.
_DEFAULT_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.db")
DB_PATH = os.environ.get("HPC_DB_PATH", _DEFAULT_DB)


def get_db() -> sqlite3.Connection:
    """요청/호출마다 NEW connection 을 연다 (결정 1A).

    - check_same_thread=False: FastAPI 워커 스레드에서 안전하게 사용.
    - row_factory=Row: dict 처럼 컬럼명 접근.
    - WAL + busy_timeout: 데모 중 'database is locked' 차단.
    호출 측은 사용 후 conn.close() 책임 (또는 db_dep 의존성 사용).
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn


def db_dep():
    """FastAPI 의존성: connection 을 yield 하고 자동으로 닫는다."""
    conn = get_db()
    try:
        yield conn
    finally:
        conn.close()


# ── 6 §DDL — 8개 테이블 (SPEC 그대로) ────────────────────────────────────────
_SCHEMA = """
CREATE TABLE IF NOT EXISTS nodes (
  node TEXT PRIMARY KEY,
  status TEXT NOT NULL,
  cpu INTEGER NOT NULL,
  gpu INTEGER NOT NULL,
  mem INTEGER NOT NULL,
  gpu_model TEXT
);

CREATE TABLE IF NOT EXISTS jobs (
  job_id TEXT PRIMARY KEY,
  user TEXT NOT NULL,
  node TEXT NOT NULL,
  purpose TEXT,
  status TEXT NOT NULL,
  elapsed TEXT
);

CREATE TABLE IF NOT EXISTS node_usage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  node TEXT NOT NULL,
  user TEXT NOT NULL,
  purpose TEXT NOT NULL,
  eta TEXT,
  source TEXT NOT NULL DEFAULT 'manual',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS servers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  os TEXT,
  spec TEXT,
  modules TEXT,
  ssh TEXT
);

CREATE TABLE IF NOT EXISTS posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  author TEXT NOT NULL,
  body TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sender TEXT NOT NULL,
  body TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS node_health (
  node TEXT PRIMARY KEY,
  temp INTEGER NOT NULL,
  disk_status TEXT NOT NULL,
  nfs_status TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS usage_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  node TEXT NOT NULL,
  user TEXT NOT NULL,
  gpu_hours REAL NOT NULL,
  day TEXT NOT NULL
);
"""


def init_db() -> None:
    """모든 테이블을 멱등 생성 (결정 2A). 여러 번 호출해도 안전."""
    conn = get_db()
    try:
        conn.executescript(_SCHEMA)
        conn.commit()
    finally:
        conn.close()


def _count(conn: sqlite3.Connection, table: str) -> int:
    return conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()["c"]


def seed_if_empty() -> None:
    """비어 있는 테이블에만 시드 (결정 2A).

    usage_log / servers / posts 를 시드해 통계·위키가 빈 화면이 아니게 한다.
    nodes / jobs / node_health 는 컬렉터가 채우므로 여기서 건드리지 않는다.
    사용자 생성 데이터(messages, node_usage)는 절대 시드/삭제하지 않는다.
    """
    conn = get_db()
    try:
        # usage_log — 노드별/사용자별/추이 집계용 시드 (node01..node08 사용)
        if _count(conn, "usage_log") == 0:
            usage_rows = [
                ("node01", "kim", 12.5, "2026-06-28"),
                ("node02", "lee", 4.0, "2026-06-28"),
                ("node04", "kim", 20.0, "2026-06-29"),
                ("node04", "park", 8.5, "2026-06-29"),
                ("node05", "choi", 6.0, "2026-06-29"),
                ("node07", "lee", 15.0, "2026-06-30"),
                ("node08", "park", 9.0, "2026-06-30"),
                ("node02", "kim", 3.5, "2026-06-30"),
            ]
            conn.executemany(
                "INSERT INTO usage_log (node, user, gpu_hours, day) VALUES (?,?,?,?)",
                usage_rows,
            )

        # servers — 위키 서버 환경 카드
        if _count(conn, "servers") == 0:
            server_rows = [
                ("gpu-cluster", "Ubuntu 22.04", "8x A100 80GB / 512GB RAM",
                 "cuda/12.2, openmpi/4.1, python/3.11", "ssh user@gpu-cluster.local"),
                ("cpu-farm", "Rocky Linux 9", "2x EPYC 64-core / 256GB RAM",
                 "gcc/13, openmpi/4.1, intel-mkl", "ssh user@cpu-farm.local"),
                ("storage-nfs", "TrueNAS", "200TB NFS shared scratch",
                 "nfs-utils", "mount -t nfs storage-nfs:/scratch /mnt/scratch"),
            ]
            conn.executemany(
                "INSERT INTO servers (name, os, spec, modules, ssh) VALUES (?,?,?,?,?)",
                server_rows,
            )

        # posts — 노하우 게시판 시드
        if _count(conn, "posts") == 0:
            now = datetime.now().isoformat()
            post_rows = [
                ("sbatch 기본 사용법", "kim",
                 "sbatch run.sh 로 작업 제출. --gres=gpu:1 로 GPU 요청.", now),
                ("mpirun 직접 실행 시 주의", "lee",
                 "스케줄러 큐에 안 잡히니 모니터링 node_usage 폼에 source=mpirun 으로 등록해 공유.", now),
                ("NFS 마운트 끊겼을 때", "park",
                 "시스템 상태 페이지에서 nfs_status 확인 후 mount -a 재시도.", now),
            ]
            conn.executemany(
                "INSERT INTO posts (title, author, body, created_at) VALUES (?,?,?,?)",
                post_rows,
            )

        conn.commit()
    finally:
        conn.close()


def upsert_nodes(rows) -> None:
    """컬렉터 결과로 nodes 테이블 upsert (PK=node, INSERT OR REPLACE)."""
    conn = get_db()
    try:
        conn.executemany(
            "INSERT OR REPLACE INTO nodes (node, status, cpu, gpu, mem, gpu_model) "
            "VALUES (:node, :status, :cpu, :gpu, :mem, :gpu_model)",
            rows,
        )
        conn.commit()
    finally:
        conn.close()


def upsert_jobs(rows) -> None:
    """컬렉터 결과로 jobs 테이블 upsert (PK=job_id)."""
    conn = get_db()
    try:
        conn.executemany(
            "INSERT OR REPLACE INTO jobs (job_id, user, node, purpose, status, elapsed) "
            "VALUES (:job_id, :user, :node, :purpose, :status, :elapsed)",
            rows,
        )
        conn.commit()
    finally:
        conn.close()


def upsert_health(rows) -> None:
    """컬렉터 결과로 node_health 테이블 upsert (PK=node)."""
    conn = get_db()
    try:
        conn.executemany(
            "INSERT OR REPLACE INTO node_health (node, temp, disk_status, nfs_status, updated_at) "
            "VALUES (:node, :temp, :disk_status, :nfs_status, :updated_at)",
            rows,
        )
        conn.commit()
    finally:
        conn.close()
