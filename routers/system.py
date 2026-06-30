"""
[팀원2] 시스템 상태 라우터 — 노드별 온도/디스크/NFS 점검 (SPEC §3.5·§6·§7.4 정합).

- 소유 파일: routers/system.py
- 테이블   : node_health(node, temp, disk_status, nfs_status, updated_at)   ← SPEC §6 잠금 스키마
- API      : GET /api/system/health   → [{node, temp, disk_status, nfs_status, updated_at}]
             GET /api/system/history  → 온도 추이(추가기능, 자기완결 확장)
- 데이터   : data/sample_health.txt 를 시작 시 1회 파싱해 적재 (SPEC §6.2 포맷)

SPEC §13 잠금 반영:
- 1A get_db 동시성 표준(요청별 연결 + check_same_thread=False + WAL + busy_timeout). 통합 시 팀장 db.py 자동 사용.
- 2A 멱등 초기화(CREATE TABLE IF NOT EXISTS + upsert/빈테이블시드).
- 5A 파서 입력 가드(헤더/빈줄 skip, 칸수 검증, int try/except → 부팅 무중단).
독립 동작: 다른 사람 코드 없이 /docs 단독 응답.
"""
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/api/system", tags=["system"])

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "sample_health.txt"

# ── 1A: DB 연결 — 통합 시 팀장 공통 helper(get_db) 우선, 없으면 동일 표준의 로컬 폴백 ──
try:
    from db import get_db  # type: ignore  # 팀장 공통 모듈(통합 시점)
except Exception:
    DB_PATH = ROOT / "hpc.db"

    def get_db():
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn


def _ensure_table(conn):
    # 2A: 멱등 — IF NOT EXISTS. SPEC §6 잠금 스키마(gpu_temp/mem 없음).
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS node_health(
            node        TEXT PRIMARY KEY,
            temp        INTEGER NOT NULL,
            disk_status TEXT    NOT NULL,
            nfs_status  TEXT    NOT NULL,
            updated_at  TEXT    NOT NULL
        )
        """
    )
    conn.commit()


def parse_health_lines(lines):
    """5A 파서 입력 가드: 헤더/빈 줄 skip, 칸 수 검증, int() try/except → 깨진 행은 건너뜀.

    SPEC §6.2 포맷(공백 구분, 위치 기반):
        NODE TEMP DISK_STATUS NFS_STATUS UPDATED_AT
        node01 42 ok ok 2026-06-30T14:00:00
    UPDATED_AT(5번째)는 선택. 어떤 입력에도 예외로 죽지 않는다.
    """
    rows = []
    for raw in lines:
        line = (raw or "").strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts[0].upper() == "NODE":   # 헤더 행 skip
            continue
        if len(parts) < 4:               # node temp disk nfs (updated_at 선택)
            continue
        try:
            temp = int(parts[1])
        except (ValueError, IndexError):
            continue                     # 잘못된 온도 → 행 skip(부팅 무중단)
        rows.append({
            "node": parts[0],
            "temp": temp,
            "disk_status": parts[2],
            "nfs_status": parts[3],
            "updated_at": parts[4] if len(parts) >= 5 else None,
        })
    return rows


def load_health():
    """sample_health.txt 파싱 → node_health upsert(멱등). 파일 없으면 최소 시드(단독 동작 보장)."""
    conn = get_db()
    _ensure_table(conn)
    now = datetime.now().isoformat(timespec="seconds")
    if DATA_FILE.exists():
        rows = parse_health_lines(DATA_FILE.read_text(encoding="utf-8").splitlines())
    else:
        rows = [{"node": f"node{i:02d}", "temp": 45, "disk_status": "ok",
                 "nfs_status": "ok", "updated_at": now} for i in range(1, 9)]
    for r in rows:
        conn.execute(
            "INSERT OR REPLACE INTO node_health(node,temp,disk_status,nfs_status,updated_at) "
            "VALUES(?,?,?,?,?)",
            (r["node"], r["temp"], r["disk_status"], r["nfs_status"], r["updated_at"] or now),
        )
    conn.commit()
    conn.close()
    return len(rows)


# ── 추가기능(자기완결 확장): CPU 온도 추이 이력 ──
def _ensure_history(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS health_history(
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            ts   TEXT    NOT NULL,
            node TEXT    NOT NULL,
            temp INTEGER NOT NULL
        )
        """
    )
    conn.commit()


def seed_history(points=30, gap_min=2):
    """2A: 비었을 때만 시드. 현재 node_health 기준 과거 온도 스냅샷 생성(차트 초기 채움)."""
    conn = get_db()
    _ensure_history(conn)
    if conn.execute("SELECT COUNT(*) AS c FROM health_history").fetchone()["c"] > 0:
        conn.close()
        return 0
    base = conn.execute("SELECT node,temp FROM node_health ORDER BY node").fetchall()
    rng = random.Random(7)
    now = datetime.now()
    count = 0
    for i in range(points, 0, -1):
        ts = (now - timedelta(minutes=gap_min * i)).isoformat(timespec="seconds")
        for b in base:
            conn.execute(
                "INSERT INTO health_history(ts,node,temp) VALUES(?,?,?)",
                (ts, b["node"], max(20, b["temp"] + rng.randint(-4, 4))),
            )
            count += 1
    conn.commit()
    conn.close()
    return count


def _maybe_record(conn, rows, gap_sec=20):
    """폴링 시 일정 간격(기본 20초)으로만 현재 온도를 이력에 추가 → 추이 live 확장."""
    _ensure_history(conn)
    last = conn.execute("SELECT MAX(ts) AS m FROM health_history").fetchone()["m"]
    now = datetime.now()
    if last:
        try:
            if (now - datetime.fromisoformat(last)).total_seconds() < gap_sec:
                return
        except ValueError:
            pass
    ts = now.isoformat(timespec="seconds")
    for r in rows:
        conn.execute("INSERT INTO health_history(ts,node,temp) VALUES(?,?,?)",
                     (ts, r["node"], r["temp"]))
    conn.commit()


# 모듈 로드 시 1회 적재 (SPEC §5.1 '앱 시작 시 1회 파싱')
load_health()
seed_history()


@router.get("/health")
def get_health(live: bool = False):
    """노드별 온도·디스크·NFS 상태 목록(node01~08). SPEC §7.4 스키마.

    live=True: 폴링 시 살아있는 느낌을 위해 temp에만 ±1 미세 변동(저장 안 함, 표시용 옵션).
    임계 판정/색상은 화면(system.html)이 처리 — 서버는 데이터만 제공.
    """
    conn = get_db()
    _ensure_table(conn)
    out = [dict(r) for r in conn.execute(
        "SELECT node,temp,disk_status,nfs_status,updated_at FROM node_health ORDER BY node"
    ).fetchall()]
    if live:
        for d in out:
            d["temp"] = max(20, d["temp"] + random.randint(-1, 1))
    _maybe_record(conn, out)
    conn.close()
    return out


@router.get("/history")
def get_history(points: int = 40):
    """온도 추이(추가기능): 시점별 CPU 온도 평균/최고 시계열. labels는 ISO, 화면이 HH:MM 표기."""
    conn = get_db()
    _ensure_history(conn)
    rows = conn.execute(
        "SELECT ts, ROUND(AVG(temp),1) AS avg, MAX(temp) AS max "
        "FROM health_history GROUP BY ts ORDER BY ts"
    ).fetchall()
    rows = rows[-points:]
    conn.close()
    return {
        "labels": [r["ts"] for r in rows],
        "avg": [r["avg"] for r in rows],
        "max": [r["max"] for r in rows],
    }
