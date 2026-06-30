"""앱 진입점 (팀장 소유) — 라우터 5개 등록 · 정적 서빙 · 컬렉터 구동.

엔지니어링 잠금 결정 반영:
- 1A/2A: startup 에서 init_db() + seed_if_empty() (멱등).
- 결정 A: 컬렉터를 1회 구동해 nodes/jobs/health upsert + 5초 주기 백그라운드 새로고침.
- 컬렉터 이름은 env COLLECTOR (기본 "mock").
"""
from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from db import init_db, seed_if_empty, upsert_nodes, upsert_jobs, upsert_health
from collectors import get_collector
from routers import monitoring, wiki, chat, stats, system

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hpc-portal")

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_STATIC_DIR = os.path.join(_BASE_DIR, "static")

REFRESH_SECONDS = 5  # 백그라운드 컬렉터 새로고침 주기


def run_collector_once() -> None:
    """설정된 컬렉터로 nodes/jobs/health 를 한 번 수집해 upsert."""
    name = os.environ.get("COLLECTOR", "mock")
    collector = get_collector(name)
    try:
        nodes = collector.collect_nodes()
        if nodes:
            upsert_nodes(nodes)
        jobs = collector.collect_jobs()
        if jobs:
            upsert_jobs(jobs)
        health = collector.collect_health()
        if health:
            upsert_health(health)
        logger.info("컬렉터(%s) 수집 완료: nodes=%d jobs=%d health=%d",
                    name, len(nodes), len(jobs), len(health))
    except Exception as exc:  # 컬렉터 오류로 앱이 죽지 않게 방어
        logger.exception("컬렉터 구동 중 오류 (무시하고 계속): %s", exc)


async def _periodic_refresh() -> None:
    """REFRESH_SECONDS 마다 컬렉터를 재구동 (cancel-safe)."""
    try:
        while True:
            await asyncio.sleep(REFRESH_SECONDS)
            # blocking sqlite/IO 는 스레드로 — 이벤트 루프 차단 방지
            await asyncio.to_thread(run_collector_once)
    except asyncio.CancelledError:
        logger.info("백그라운드 새로고침 종료")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── startup ──
    init_db()
    seed_if_empty()
    run_collector_once()  # 최초 1회 즉시 적재
    refresh_task = asyncio.create_task(_periodic_refresh())
    try:
        yield
    finally:
        # ── shutdown (cancel-safe) ──
        refresh_task.cancel()
        try:
            await refresh_task
        except asyncio.CancelledError:
            pass


app = FastAPI(title="사내 HPC 통합 포털", version="1.0", lifespan=lifespan)

# 라우터 5개 등록 (각 라우터가 /api 프리픽스를 보유)
app.include_router(monitoring.router)
app.include_router(wiki.router)
app.include_router(chat.router)
app.include_router(stats.router)
app.include_router(system.router)


@app.get("/")
def index():
    """랜딩 페이지 (채팅 위젯 미포함)."""
    return FileResponse(os.path.join(_STATIC_DIR, "index.html"))


# 정적 파일 서빙 (HTML/CSS/JS) — /static/*
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")
