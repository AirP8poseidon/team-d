"""
[팀원2] 사용량 통계 라우터 — 노드별/사용자별 GPU 사용량 집계·추이.

- 소유 파일: routers/stats.py (DEV_BLUEPRINT §3)
- 테이블   : usage_log (DEV_BLUEPRINT §4) — 자체 시드(팀장 테이블 비의존 → 독립)
- API      : GET /api/stats/usage → {byNode, byUser, trend}

독립 동작: 자체 테이블 생성 + 시드로 `/docs` 단독 응답.
통합 시  : 팀장 db.py 의 get_conn() 이 있으면 자동 사용(공통 DB 파일 공유).
"""
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/api/stats", tags=["stats"])

ROOT = Path(__file__).resolve().parent.parent

try:
    from db import get_conn  # type: ignore  # 팀장 공통 모듈(통합 시점)
except Exception:
    DB_PATH = ROOT / "hpc.db"

    def get_conn():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn


NODES = [f"node{i:02d}" for i in range(1, 9)]   # node01~08 (통합 키)
USERS = ["김지훈", "이서연", "박민수", "정유진", "최현우"]


def _ensure_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS usage_log(
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            node      TEXT,
            user      TEXT,
            gpu_hours REAL,
            day       TEXT
        )
        """
    )
    conn.commit()


def seed(days=7):
    """통계용 시드(독립). 이미 데이터가 있으면 건너뜀(재실행 안전)."""
    conn = get_conn()
    _ensure_table(conn)
    have = conn.execute("SELECT COUNT(*) AS c FROM usage_log").fetchone()["c"]
    if have > 0:
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
    """사용량 집계: 노드별 / 사용자별 / 일자별 추이 + 요약 지표 + 노드×사용자 구성(스택)."""
    conn = get_conn()
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

    # 추가 통계: 노드×사용자 구성(스택 막대용)
    nodes = [r["node"] for r in by_node]
    users = [r["user"] for r in by_user]
    cells = {(r["node"], r["user"]): r["h"] for r in conn.execute(
        "SELECT node, user, ROUND(SUM(gpu_hours),1) AS h "
        "FROM usage_log GROUP BY node, user"
    ).fetchall()}
    stacked = [{"user": u, "data": [cells.get((n, u), 0) for n in nodes]} for u in users]

    # 추가 통계: 요약 지표
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
        "byNode": by_node,
        "byUser": by_user,
        "trend": trend,
        "stacked": {"nodes": nodes, "series": stacked},
        "summary": summary,
    }
