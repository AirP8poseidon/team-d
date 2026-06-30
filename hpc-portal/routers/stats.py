"""통계 라우터 (팀원2 소유) — /api/stats/*.

SPEC §7.4:
  GET /api/stats/usage     -> {by_node, by_user, trend, summary}
확장(FR-S3):
  GET /api/stats/capacity  -> {references:[{key,label,cutoff,users:[{user,gpu_hours}]}]}
                              사용자별 누적 용량(GPU-hours)을 기준 시점별로
                              (오늘 00시 / 3일전 / 1주일전 / 현재시각).

usage_log 는 db.py seed_if_empty() 가 기본 시드한다. 추이를 '1주일 이전부터' 보이도록
최근 8일 범위에서 비어 있는 날만 멱등 보충(_ensure_week_usage) — usage_log 는 팀원2 소유.
"""
from __future__ import annotations

import random
from datetime import date, timedelta

from fastapi import APIRouter, Depends

from db import db_dep, NODES

router = APIRouter(prefix="/api/stats", tags=["stats"])

USERS = ["kim", "lee", "park", "choi"]


def _ensure_week_usage(db, days=7):
    """추이가 최근 1주일을 포함하도록 비어 있는 날만 멱등 보충(2A). 기존 시드는 보존."""
    today = date.today()
    for i in range(days, -1, -1):
        day = (today - timedelta(days=i)).isoformat()
        if db.execute("SELECT COUNT(*) AS c FROM usage_log WHERE day=?", (day,)).fetchone()["c"] > 0:
            continue
        rng = random.Random(int(day.replace("-", "")))  # 날짜 기반 결정적 시드
        for _ in range(rng.randint(2, 4)):
            db.execute(
                "INSERT INTO usage_log(node, user, gpu_hours, day) VALUES(?,?,?,?)",
                (rng.choice(NODES), rng.choice(USERS), round(rng.uniform(2.0, 18.0), 1), day),
            )
    db.commit()


@router.get("/usage")
def get_usage(db=Depends(db_dep)):
    """노드별·사용자별 집계 + 일자별 추이(최근 1주일+) + 요약."""
    _ensure_week_usage(db)
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

    total = round(sum(r["gpu_hours"] for r in by_node), 2)
    days = [r["day"] for r in trend]
    peak = max(trend, key=lambda r: r["gpu_hours"]) if trend else {"day": "-", "gpu_hours": 0}
    summary = {
        "total": total,
        "avgPerDay": round(total / len(days), 2) if days else 0,
        "peakDay": peak["day"],
        "peakHours": peak["gpu_hours"],
        "activeUsers": len(by_user),
        "activeNodes": len([n for n in by_node if n["gpu_hours"] > 0]),
        "days": len(days),
    }
    return {"by_node": by_node, "by_user": by_user, "trend": trend, "summary": summary}


@router.get("/capacity")
def get_capacity(db=Depends(db_dep)):
    """사용자별 누적 용량(GPU-hours)을 기준 시점별로 — 오늘 00시/3일전/1주일전/현재시각.

    누적 = 해당 기준일까지(day <= cutoff)의 사용자별 gpu_hours 합.
    '오늘 00시' = 어제까지 누적, '현재시각' = 오늘 포함.
    """
    _ensure_week_usage(db)
    today = date.today()
    refs = [
        ("w1", "1주일전", (today - timedelta(days=7)).isoformat()),
        ("d3", "3일전", (today - timedelta(days=3)).isoformat()),
        ("today", "오늘 00시", (today - timedelta(days=1)).isoformat()),
        ("now", "현재시각", today.isoformat()),
    ]
    out = []
    for key, label, cutoff in refs:
        users = [dict(r) for r in db.execute(
            "SELECT user, ROUND(SUM(gpu_hours),2) AS gpu_hours FROM usage_log "
            "WHERE day <= ? GROUP BY user ORDER BY gpu_hours DESC", (cutoff,)
        ).fetchall()]
        out.append({"key": key, "label": label, "cutoff": cutoff, "users": users})
    return {"references": out}
