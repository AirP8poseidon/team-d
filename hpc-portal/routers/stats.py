"""통계 라우터 (팀원2 소유) — /api/stats/*.

SPEC §7.4:
  GET /api/stats/usage -> {by_node, by_user, trend}
확장(FR-S3 '추가 아이디어 캐치올' — 핵심 키는 그대로 유지):
  + summary  (총·일평균·최번일·활성 사용자/노드 등)
  + stacked  (노드×사용자 구성, 스택 막대용)

usage_log 는 db.py seed_if_empty() 가 시드한다(읽기 모델).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from db import db_dep

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/usage")
def get_usage(db=Depends(db_dep)):
    """노드별·사용자별 집계 + 일자별 추이 + (확장) summary / stacked."""
    by_node = [dict(r) for r in db.execute(
        "SELECT node, ROUND(SUM(gpu_hours),2) AS gpu_hours "
        "FROM usage_log GROUP BY node ORDER BY node"
    ).fetchall()]
    by_user = [dict(r) for r in db.execute(
        "SELECT user, ROUND(SUM(gpu_hours),2) AS gpu_hours "
        "FROM usage_log GROUP BY user ORDER BY gpu_hours DESC"
    ).fetchall()]
    trend = [dict(r) for r in db.execute(
        "SELECT day, ROUND(SUM(gpu_hours),2) AS gpu_hours "
        "FROM usage_log GROUP BY day ORDER BY day"
    ).fetchall()]

    # 확장(FR-S3): 노드×사용자 구성(스택 막대용)
    nodes = [r["node"] for r in by_node]
    users = [r["user"] for r in by_user]
    cells = {(r["node"], r["user"]): r["h"] for r in db.execute(
        "SELECT node, user, ROUND(SUM(gpu_hours),2) AS h FROM usage_log GROUP BY node, user"
    ).fetchall()}
    stacked = [{"user": u, "data": [cells.get((n, u), 0) for n in nodes]} for u in users]

    # 확장(FR-S3): 요약 지표
    total = round(sum(r["gpu_hours"] for r in by_node), 2)
    days = [r["day"] for r in trend]
    peak = max(trend, key=lambda r: r["gpu_hours"]) if trend else {"day": "-", "gpu_hours": 0}
    summary = {
        "total": total,
        "avgPerDay": round(total / len(days), 2) if days else 0,
        "peakDay": peak["day"],
        "peakHours": peak["gpu_hours"],
        "activeUsers": len(users),
        "activeNodes": len([n for n in by_node if n["gpu_hours"] > 0]),
        "days": len(days),
    }
    return {
        "by_node": by_node,
        "by_user": by_user,
        "trend": trend,
        "stacked": {"nodes": nodes, "series": stacked},
        "summary": summary,
    }
