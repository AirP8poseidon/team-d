"""통계 라우터 (팀원2 소유) — /api/stats/*.

SPEC §7.4:
  GET /api/stats/usage     -> {by_node, by_user, trend, summary}
확장(FR-S3):
  GET /api/stats/capacity  -> {references:[{key,label,cutoff,users:[{user,used_gb}]}]}
                              사용자별 '스토리지 사용량(GB)'을 기준 시점별 스냅샷으로
                              (오늘 00시 / 3일전 / 1주일전 / 현재시각).

usage_log 는 db.py seed_if_empty() 가 기본 시드한다. 추이를 '1주일 이전부터' 보이도록
최근 8일 범위에서 비어 있는 날만 멱등 보충(_ensure_week_usage) — usage_log 는 팀원2 소유.
스토리지 용량은 GPU-hours 와 무관한 점유 용량이라 자기완결 user_storage 테이블로 분리
(db.py 미수정, 노드/온도와 함께 '운영 가시성' 지표).
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


# 사용자별 기준 스토리지 점유 용량(GB) — 결정적. 스토리지는 시간이 갈수록 누적 증가.
_STORAGE_BASE = {"kim": 820.0, "lee": 540.0, "park": 1180.0, "choi": 360.0}
# 사용자별 스토리지 쿼터(GB) — 사용률·임계 색상의 기준(직관적 게이지용).
_STORAGE_QUOTA = {"kim": 1500.0, "lee": 1000.0, "park": 2000.0, "choi": 1000.0}


def _ensure_user_storage(db, days=7):
    """사용자별 스토리지 사용량(GB) 일별 스냅샷을 멱등 보충(2A). 자기완결 테이블(db.py 미수정).

    스냅샷(누적합 아님) = 그 날의 사용자별 디스크 점유 용량. 과거→현재로 단조 증가 경향.
    날짜·사용자 기반 결정적 시드라 재시작해도 동일.
    """
    db.execute(
        "CREATE TABLE IF NOT EXISTS user_storage("
        "user TEXT NOT NULL, day TEXT NOT NULL, used_gb REAL NOT NULL, "
        "PRIMARY KEY(user, day))"
    )
    today = date.today()
    for i in range(days, -1, -1):
        day = (today - timedelta(days=i)).isoformat()
        if db.execute("SELECT COUNT(*) AS c FROM user_storage WHERE day=?", (day,)).fetchone()["c"] > 0:
            continue
        elapsed = days - i  # 0(가장 과거)..days(오늘)
        for idx, u in enumerate(USERS):
            rng = random.Random(int(day.replace("-", "")) + idx * 131)  # 날짜·사용자 결정적
            val = _STORAGE_BASE.get(u, 400.0) + elapsed * rng.uniform(3.0, 12.0) + rng.uniform(-2.0, 2.0)
            db.execute(
                "INSERT INTO user_storage(user, day, used_gb) VALUES(?,?,?)",
                (u, day, round(max(0.0, val), 1)),
            )
    db.commit()


@router.get("/capacity")
def get_capacity(db=Depends(db_dep)):
    """사용자별 스토리지 사용량(GB)을 기준 시점별 스냅샷으로 — 1주일전/3일전/오늘 00시/현재시각.

    누적합이 아니라 그 시점의 디스크 점유 용량(GB) + 쿼터 대비 사용률(%).
    '오늘 00시'=어제 스냅샷, '현재시각'=오늘. 사용률 높은 순으로 정렬(쿼터 임박 사용자 먼저).
    """
    _ensure_user_storage(db)
    today = date.today()
    refs = [
        ("w1", "1주일전", (today - timedelta(days=7)).isoformat()),
        ("d3", "3일전", (today - timedelta(days=3)).isoformat()),
        ("today", "오늘 00시", (today - timedelta(days=1)).isoformat()),
        ("now", "현재시각", today.isoformat()),
    ]
    out = []
    for key, label, cutoff in refs:
        # 기준일 이하 가장 최근 스냅샷(보통 그 날 자체)
        rows = db.execute(
            "SELECT user, used_gb FROM user_storage "
            "WHERE day = (SELECT MAX(day) FROM user_storage WHERE day <= ?)", (cutoff,)
        ).fetchall()
        users = []
        for r in rows:
            quota = _STORAGE_QUOTA.get(r["user"], 1000.0)
            users.append({
                "user": r["user"],
                "used_gb": r["used_gb"],
                "quota_gb": quota,
                "used_pct": round(r["used_gb"] / quota * 100, 1) if quota else 0,
            })
        users.sort(key=lambda u: u["used_pct"], reverse=True)
        out.append({"key": key, "label": label, "cutoff": cutoff, "users": users})
    return {"references": out}
