"""
[팀원2] 사용량 통계 라우터 — 노드별/사용자별 GPU 사용량 집계·추이 (SPEC §3.4·§6·§7.4 정합).

- 소유 파일: routers/stats.py
- 테이블   : usage_log(id, node, user, gpu_hours, day)   ← SPEC §6 잠금 스키마(자체 시드 → 독립)
- API      : GET /api/stats/usage → {by_node, by_user, trend}  (SPEC §7.4 키 정합)
             + summary, stacked (FR-S3 '추가 아이디어 캐치올' 확장 — 핵심 키는 그대로 유지)

SPEC §13: 1A get_db 표준 / 2A 멱등 시드(비었을 때만).
독립 동작: 자체 테이블 생성 + 시드로 /docs 단독 응답.
"""
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/api/stats", tags=["stats"])

ROOT = Path(__file__).resolve().parent.parent

# ── 1A: DB 연결 — 통합 시 팀장 get_db 우선, 없으면 동일 표준 로컬 폴백 ──
try:
    from db import get_db  # type: ignore
except Exception:
    DB_PATH = ROOT / "hpc.db"

    def get_db():
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn


NODES = [f"node{i:02d}" for i in range(1, 9)]   # node01~08 (통합 키)
USERS = ["김지훈", "이서연", "박민수", "정유진", "최현우"]


def _ensure_table(conn):
    # 2A 멱등 + SPEC §6 잠금 스키마(NOT NULL)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS usage_log(
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            node      TEXT NOT NULL,
            user      TEXT NOT NULL,
            gpu_hours REAL NOT NULL,
            day       TEXT NOT NULL
        )
        """
    )
    conn.commit()


def seed(days=7):
    """2A: 비었을 때만 시드(재실행 안전). 자체 데이터 → 팀장 테이블 비의존(독립)."""
    conn = get_db()
    _ensure_table(conn)
    if conn.execute("SELECT COUNT(*) AS c FROM usage_log").fetchone()["c"] > 0:
        conn.close()
        return 0
    rng = random.Random(42)  # 재현성 고정 시드
    today = date.today()
    count = 0
    for d in range(days):
        day = (today - timedelta(days=days - 1 - d)).isoformat()
        for node in NODES:
            for _ in range(rng.randint(1, 3)):   # 노드별 1~3건/일
                conn.execute(
                    "INSERT INTO usage_log(node,user,gpu_hours,day) VALUES(?,?,?,?)",
                    (node, rng.choice(USERS), round(rng.uniform(0.5, 12.0), 1), day),
                )
                count += 1
    conn.commit()
    conn.close()
    return count


# 모듈 로드 시 1회 시드
seed()


@router.get("/usage")
def get_usage():
    """사용량 집계 (SPEC §7.4): by_node / by_user / trend + (확장) summary / stacked."""
    conn = get_db()
    _ensure_table(conn)
    by_node = [dict(r) for r in conn.execute(
        "SELECT node, ROUND(SUM(gpu_hours),1) AS gpu_hours "
        "FROM usage_log GROUP BY node ORDER BY node"
    ).fetchall()]
    by_user = [dict(r) for r in conn.execute(
        "SELECT user, ROUND(SUM(gpu_hours),1) AS gpu_hours "
        "FROM usage_log GROUP BY user ORDER BY gpu_hours DESC"
    ).fetchall()]
    trend = [dict(r) for r in conn.execute(
        "SELECT day, ROUND(SUM(gpu_hours),1) AS gpu_hours "
        "FROM usage_log GROUP BY day ORDER BY day"
    ).fetchall()]

    # 확장(FR-S3): 노드×사용자 구성(스택 막대용)
    nodes = [r["node"] for r in by_node]
    users = [r["user"] for r in by_user]
    cells = {(r["node"], r["user"]): r["h"] for r in conn.execute(
        "SELECT node, user, ROUND(SUM(gpu_hours),1) AS h FROM usage_log GROUP BY node, user"
    ).fetchall()}
    stacked = [{"user": u, "data": [cells.get((n, u), 0) for n in nodes]} for u in users]

    # 확장(FR-S3): 요약 지표
    total = round(sum(r["gpu_hours"] for r in by_node), 1)
    days = [r["day"] for r in trend]
    peak = max(trend, key=lambda r: r["gpu_hours"]) if trend else {"day": "-", "gpu_hours": 0}
    summary = {
        "total": total,
        "avgPerDay": round(total / len(days), 1) if days else 0,
        "peakDay": peak["day"],
        "peakHours": peak["gpu_hours"],
        "activeUsers": len(users),
        "activeNodes": len([n for n in by_node if n["gpu_hours"] > 0]),
        "days": len(days),
    }
    conn.close()
    return {
        "by_node": by_node,
        "by_user": by_user,
        "trend": trend,
        "stacked": {"nodes": nodes, "series": stacked},
        "summary": summary,
    }
