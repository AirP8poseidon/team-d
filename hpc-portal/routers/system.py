"""시스템 상태 라우터 (팀원2 소유) — /api/system/*.

스켈레톤: node_health 표출. SPEC §7.4 그대로.
  GET /api/system/health -> [{node, temp, disk_status, nfs_status, updated_at}]
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from db import db_dep

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/health")
def get_health(db=Depends(db_dep)):
    """노드별 온도·디스크·NFS 상태 (node01..08)."""
    rows = db.execute(
        "SELECT node, temp, disk_status, nfs_status, updated_at "
        "FROM node_health ORDER BY node"
    ).fetchall()
    return [dict(r) for r in rows]
