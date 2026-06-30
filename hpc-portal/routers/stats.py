"""통계 라우터 (팀원2 소유) — /api/stats/*.

스켈레톤: usage_log 집계. SPEC §7.4 응답 형태 그대로.
  GET /api/stats/usage -> {by_node:[{node, gpu_hours}],
                           by_user:[{user, gpu_hours}],
                           trend:[{day, gpu_hours}]}
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from db import db_dep

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/usage")
def get_usage(db=Depends(db_dep)):
    """노드별·사용자별 집계 + 일자별 추이."""
    by_node = db.execute(
        "SELECT node, ROUND(SUM(gpu_hours), 2) AS gpu_hours "
        "FROM usage_log GROUP BY node ORDER BY node"
    ).fetchall()
    by_user = db.execute(
        "SELECT user, ROUND(SUM(gpu_hours), 2) AS gpu_hours "
        "FROM usage_log GROUP BY user ORDER BY gpu_hours DESC"
    ).fetchall()
    trend = db.execute(
        "SELECT day, ROUND(SUM(gpu_hours), 2) AS gpu_hours "
        "FROM usage_log GROUP BY day ORDER BY day"
    ).fetchall()
    return {
        "by_node": [dict(r) for r in by_node],
        "by_user": [dict(r) for r in by_user],
        "trend": [dict(r) for r in trend],
    }
