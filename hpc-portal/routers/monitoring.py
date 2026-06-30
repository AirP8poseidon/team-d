"""모니터링 라우터 (팀장 소유) — /api/monitoring/*.

엔드포인트 (SPEC §7.1):
  GET  /api/monitoring/nodes        노드 상태·자원
  GET  /api/monitoring/jobs         job 큐
  GET  /api/monitoring/usage        작업 맥락 목록 (전체)
  GET  /api/monitoring/usage/latest 노드별 최신 1건 (결정 3A — 카드용)
  POST /api/monitoring/usage        맥락 등록 {node, user, purpose, eta, source?}
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from db import db_dep

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


class UsageIn(BaseModel):
    node: str
    user: str
    purpose: str
    eta: Optional[str] = None
    source: Optional[str] = "manual"


@router.get("/nodes")
def get_nodes(db=Depends(db_dep)):
    """node01..08 의 status·CPU·GPU·메모리·GPU모델."""
    rows = db.execute(
        "SELECT node, status, cpu, gpu, mem, gpu_model FROM nodes ORDER BY node"
    ).fetchall()
    return [dict(r) for r in rows]


@router.get("/jobs")
def get_jobs(db=Depends(db_dep)):
    """현재 작업 큐 (squeue 목업 기반)."""
    rows = db.execute(
        "SELECT job_id, user, node, purpose, status, elapsed FROM jobs ORDER BY job_id"
    ).fetchall()
    return [dict(r) for r in rows]


@router.get("/usage")
def get_usage(db=Depends(db_dep)):
    """등록된 작업 맥락 전체 (최신순)."""
    rows = db.execute(
        "SELECT id, node, user, purpose, eta, source, created_at "
        "FROM node_usage ORDER BY created_at DESC, id DESC"
    ).fetchall()
    return [dict(r) for r in rows]


@router.get("/usage/latest")
def get_usage_latest(db=Depends(db_dep)):
    """노드별 최신 작업 맥락 1건 (결정 3A — 모니터링 카드용).

    각 노드에 대해 created_at DESC 최신 1건만 반환한다.
    """
    rows = db.execute(
        """
        SELECT u.id, u.node, u.user, u.purpose, u.eta, u.source, u.created_at
        FROM node_usage u
        JOIN (
            SELECT node, MAX(id) AS max_id
            FROM node_usage
            GROUP BY node
        ) latest ON u.node = latest.node AND u.id = latest.max_id
        ORDER BY u.node
        """
    ).fetchall()
    return [dict(r) for r in rows]


@router.post("/usage")
def post_usage(payload: UsageIn, db=Depends(db_dep)):
    """작업 맥락 등록. 서버가 created_at(ISO) 생성. source 기본 'manual'."""
    created_at = datetime.now().isoformat()
    source = payload.source or "manual"
    cur = db.execute(
        "INSERT INTO node_usage (node, user, purpose, eta, source, created_at) "
        "VALUES (?,?,?,?,?,?)",
        (payload.node, payload.user, payload.purpose, payload.eta, source, created_at),
    )
    db.commit()
    return {
        "id": cur.lastrowid,
        "node": payload.node,
        "user": payload.user,
        "purpose": payload.purpose,
        "eta": payload.eta,
        "source": source,
        "created_at": created_at,
    }
