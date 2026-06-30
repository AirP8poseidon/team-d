"""
[팀원2] 시스템 상태 라우터 — 노드별 온도/디스크/NFS(+GPU온도/메모리) 점검.

- 소유 파일: routers/system.py (DEV_BLUEPRINT §3)
- 테이블   : node_health (DEV_BLUEPRINT §4, 확장 컬럼 gpu_temp/mem)
- API      : GET /api/system/health
- 데이터   : data/sample_health.txt 를 시작 시 1회 파싱해 적재 (실서버 연동 없음)

독립 동작: 다른 사람 코드 없이 `/docs` 에서 단독 응답하도록 자체 테이블 생성·적재.
통합 시  : 팀장 db.py 의 get_conn() 이 있으면 자동으로 그것을 사용(공통 DB 파일 공유).
"""
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/api/system", tags=["system"])

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "sample_health.txt"

# --- DB 연결: 통합 시 팀장 공통 모듈 우선, 없으면 로컬 폴백(독립 동작) ---
try:
    from db import get_conn  # type: ignore  # 팀장 공통 모듈(통합 시점에 존재)
except Exception:
    DB_PATH = ROOT / "hpc.db"

    def get_conn():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn


def _ensure_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS node_health(
            node        TEXT PRIMARY KEY,
            temp        INTEGER,
            gpu_temp    INTEGER,
            mem         INTEGER,
            disk_status TEXT,
            nfs_status  TEXT,
            updated_at  TEXT
        )
        """
    )
    conn.commit()


def _parse_line(line):
    """'node01 temp=42 gpu_temp=61 mem=55 disk=OK nfs=OK' → dict"""
    parts = line.split()
    kv = {}
    for tok in parts[1:]:
        if "=" in tok:
            k, v = tok.split("=", 1)
            kv[k] = v
    return {
        "node": parts[0],
        "temp": int(kv.get("temp", 0)),
        "gpu_temp": int(kv.get("gpu_temp", 0)),
        "mem": int(kv.get("mem", 0)),
        "disk_status": kv.get("disk", "OK"),
        "nfs_status": kv.get("nfs", "OK"),
    }


def load_health():
    """sample_health.txt 파싱 → node_health upsert. 파일 없으면 최소 시드(단독 동작 보장)."""
    conn = get_conn()
    _ensure_table(conn)
    now = datetime.now().isoformat(timespec="seconds")
    rows = []
    if DATA_FILE.exists():
        for raw in DATA_FILE.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            rows.append(_parse_line(line))
    else:
        for i in range(1, 9):
            rows.append({"node": f"node{i:02d}", "temp": 45, "gpu_temp": 60,
                         "mem": 50, "disk_status": "OK", "nfs_status": "OK"})
    for r in rows:
        conn.execute(
            "INSERT OR REPLACE INTO node_health"
            "(node,temp,gpu_temp,mem,disk_status,nfs_status,updated_at) "
            "VALUES(?,?,?,?,?,?,?)",
            (r["node"], r["temp"], r["gpu_temp"], r["mem"],
             r["disk_status"], r["nfs_status"], now),
        )
    conn.commit()
    conn.close()
    return len(rows)


# ── 추가기능: 상태 이력 추이 (node_health 스냅샷 누적 → 온도 추이 차트) ──
def _ensure_history(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS health_history(
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            ts       TEXT,
            node     TEXT,
            temp     INTEGER,
            gpu_temp INTEGER,
            mem      INTEGER
        )
        """
    )
    conn.commit()


def seed_history(points=30, gap_min=2):
    """비어 있으면 현재 node_health 기준으로 과거 스냅샷을 시드(차트가 처음부터 채워지도록)."""
    conn = get_conn()
    _ensure_history(conn)
    if conn.execute("SELECT COUNT(*) AS c FROM health_history").fetchone()["c"] > 0:
        conn.close()
        return 0
    base = conn.execute(
        "SELECT node,temp,gpu_temp,mem FROM node_health ORDER BY node"
    ).fetchall()
    rng = random.Random(7)  # 재현성
    now = datetime.now()
    count = 0
    for i in range(points, 0, -1):
        ts = (now - timedelta(minutes=gap_min * i)).isoformat(timespec="seconds")
        for b in base:
            conn.execute(
                "INSERT INTO health_history(ts,node,temp,gpu_temp,mem) VALUES(?,?,?,?,?)",
                (ts, b["node"],
                 max(20, b["temp"] + rng.randint(-4, 4)),
                 max(20, b["gpu_temp"] + rng.randint(-5, 5)),
                 max(0, min(100, b["mem"] + rng.randint(-6, 6)))),
            )
            count += 1
    conn.commit()
    conn.close()
    return count


def _maybe_record(conn, rows, gap_sec=20):
    """폴링 시 일정 간격(기본 20초)으로만 현재 상태를 이력에 추가 → 추이가 live 확장."""
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
        conn.execute(
            "INSERT INTO health_history(ts,node,temp,gpu_temp,mem) VALUES(?,?,?,?,?)",
            (ts, r["node"], r["temp"], r["gpu_temp"], r["mem"]),
        )
    conn.commit()


# 모듈 로드 시 1회 적재 (DEV_BLUEPRINT §1 '시작 시 1회 파싱')
load_health()
seed_history()


@router.get("/health")
def get_health(live: bool = True):
    """노드별 온도·GPU온도·메모리·디스크·NFS 상태 목록(node01~08).

    live=True: 폴링 시 살아있는 느낌을 위해 수치에 ±1 미세 변동(저장 안 함, 표시용).
    임계치 판정/색상은 화면(system.html)이 동일 기준으로 처리 — 서버는 데이터만 제공.
    """
    conn = get_conn()
    _ensure_table(conn)
    cur = conn.execute(
        "SELECT node,temp,gpu_temp,mem,disk_status,nfs_status,updated_at "
        "FROM node_health ORDER BY node"
    )
    out = []
    for row in cur.fetchall():
        d = dict(row)
        if live:
            d["temp"] = max(20, d["temp"] + random.randint(-1, 1))
            d["gpu_temp"] = max(20, d["gpu_temp"] + random.randint(-1, 1))
            d["mem"] = max(0, min(100, d["mem"] + random.randint(-1, 1)))
        out.append(d)
    _maybe_record(conn, out)   # 추이 이력에 간헐 기록(20초 간격)
    conn.close()
    return out


@router.get("/history")
def get_history(points: int = 40):
    """온도 추이(추가기능): 시점별 평균 CPU/GPU 온도 시계열. labels는 ISO, 화면이 HH:MM로 표기."""
    conn = get_conn()
    _ensure_history(conn)
    rows = conn.execute(
        "SELECT ts, ROUND(AVG(temp),1) AS cpu, ROUND(AVG(gpu_temp),1) AS gpu "
        "FROM health_history GROUP BY ts ORDER BY ts"
    ).fetchall()
    rows = rows[-points:]
    conn.close()
    return {
        "labels": [r["ts"] for r in rows],
        "cpu_avg": [r["cpu"] for r in rows],
        "gpu_avg": [r["gpu"] for r in rows],
    }
