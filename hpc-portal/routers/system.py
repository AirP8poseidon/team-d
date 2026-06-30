"""시스템 상태 라우터 (팀원2 소유) — /api/system/*.

SPEC §7.4:
  GET /api/system/health  -> [{node, temp, disk_status, nfs_status, updated_at}]
확장(FR-Y3 운영 가시성):
  GET /api/system/history -> {labels, avg, max}  # CPU 온도 추이(평균·최고)

node_health 는 컬렉터(mock)가 sample_health.txt 로 채운다(읽기 모델).
온도 추이는 자기완결 확장 테이블 health_history 로 관리 — db.py 미수정, 라우터가 멱등 생성/기록.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends

from db import db_dep

router = APIRouter(prefix="/api/system", tags=["system"])


# ── 확장: CPU 온도 추이 이력(health_history) — 라우터 자기완결 ──
def _ensure_history(db):
    db.execute(
        "CREATE TABLE IF NOT EXISTS health_history("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, "
        "node TEXT NOT NULL, temp INTEGER NOT NULL)"
    )
    db.commit()


def _seed_history_if_empty(db):
    """2A 멱등: 비었을 때만, 현재 node_health 기준 과거 스냅샷 생성(차트 초기 채움)."""
    _ensure_history(db)
    if db.execute("SELECT COUNT(*) AS c FROM health_history").fetchone()["c"] > 0:
        return
    base = db.execute("SELECT node, temp FROM node_health ORDER BY node").fetchall()
    if not base:
        return
    rng = random.Random(7)
    now = datetime.now()
    for i in range(30, 0, -1):
        ts = (now - timedelta(minutes=2 * i)).isoformat(timespec="seconds")
        for b in base:
            db.execute(
                "INSERT INTO health_history(ts, node, temp) VALUES(?,?,?)",
                (ts, b["node"], max(20, b["temp"] + rng.randint(-4, 4))),
            )
    db.commit()


def _maybe_record(db, gap_sec=20):
    """폴링 시 일정 간격(기본 20초)으로만 현재 온도를 이력에 추가 → 추이 live 확장."""
    _ensure_history(db)
    last = db.execute("SELECT MAX(ts) AS m FROM health_history").fetchone()["m"]
    now = datetime.now()
    if last:
        try:
            if (now - datetime.fromisoformat(last)).total_seconds() < gap_sec:
                return
        except ValueError:
            pass
    ts = now.isoformat(timespec="seconds")
    for r in db.execute("SELECT node, temp FROM node_health ORDER BY node").fetchall():
        db.execute("INSERT INTO health_history(ts, node, temp) VALUES(?,?,?)",
                   (ts, r["node"], r["temp"]))
    db.commit()


@router.get("/health")
def get_health(db=Depends(db_dep)):
    """노드별 온도·디스크·NFS 상태 (node01..08). SPEC §7.4 스키마."""
    rows = db.execute(
        "SELECT node, temp, disk_status, nfs_status, updated_at "
        "FROM node_health ORDER BY node"
    ).fetchall()
    _seed_history_if_empty(db)
    _maybe_record(db)
    return [dict(r) for r in rows]


@router.get("/history")
def get_history(points: int = 40, db=Depends(db_dep)):
    """CPU 온도 추이(확장): 시점별 평균/최고 온도 시계열. labels는 ISO, 화면이 HH:MM 표기."""
    _seed_history_if_empty(db)
    rows = db.execute(
        "SELECT ts, ROUND(AVG(temp),1) AS avg, MAX(temp) AS max "
        "FROM health_history GROUP BY ts ORDER BY ts"
    ).fetchall()
    rows = rows[-points:]
    return {
        "labels": [r["ts"] for r in rows],
        "avg": [r["avg"] for r in rows],
        "max": [r["max"] for r in rows],
    }
