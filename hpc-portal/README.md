# 사내 HPC 통합 포털 (hpc-portal)

FastAPI + SQLite 단일 웹앱. SLURM 자원 숫자 위에 **사람의 맥락 + 실시간 소통 + 운영 가시성**을 더한다.
이 디렉터리는 **공통 뼈대 + 데이터 수집 seam** 까지 구현된 상태이며, 팀원 소유 페이지는 헤더-only 스텁이다.

## 실행

```bash
cd hpc-portal
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# http://localhost:8000   ·   API 문서: /docs
```

시작 시 `init_db()` → `seed_if_empty()` → 컬렉터 1회 구동(nodes/jobs/health 적재)이 자동 실행되고,
이후 5초 주기 백그라운드 태스크가 컬렉터를 재구동해 새로고침한다.

## 테스트

```bash
cd hpc-portal
pytest -q
```

테스트는 `HPC_DB_PATH` 환경변수로 임시 DB 를 써서 `app.db` 를 건드리지 않는다.
(파서 정상/깨진행 · 멱등 시드 · 노드키 정합 · 라우터 200 스모크 — 결정 6A)

## 데이터 수집 seam (컬렉터 교체)

`data/sample_*.txt` 파싱은 `collectors/` 의 **MockCollector** 가 담당한다.
실서버 연동은 동일 인터페이스(`Collector` ABC)를 구현한 컬렉터를 끼우면 된다 (drop-in).

```bash
COLLECTOR=mock        uvicorn main:app   # 기본 — 샘플 파일 파싱
COLLECTOR=slurm       uvicorn main:app   # collectors/slurm.py (미구현 스텁)
COLLECTOR=prometheus  uvicorn main:app   # collectors/prometheus.py (미구현 스텁)
```

- `collectors/slurm.py` — `squeue`/`sinfo` subprocess 연동 자리.
- `collectors/prometheus.py` — Prometheus `/api/v1/query` 연동 자리.
- 알 수 없는 이름은 MockCollector 로 폴백한다.

## 파일 소유 (본인 파일만 수정)

| 담당 | 소유 파일 |
|---|---|
| **팀장(공통)** | `main.py`, `db.py`, `requirements.txt`, `static/common.css`, `static/_nav.html`, `static/include.js`, `static/index.html`, `collectors/*`, `routers/monitoring.py`, `static/monitoring.html`, `data/sample_squeue.txt`, `data/sample_sinfo.txt` |
| **팀원1** | `routers/wiki.py`, `routers/chat.py`, `static/wiki.html`, `static/chat-widget.js` |
| **팀원2** | `routers/stats.py`, `routers/system.py`, `static/stats.html`, `static/system.html`, `data/sample_health.txt` |

> 팀원 페이지(`wiki/stats/system.html`)와 `monitoring.html` 은 **헤더-only 스텁**이다.
> 각 파일의 `TODO(팀원X)` 주석을 보고 SPEC §7 에 맞춰 `fetch` 배선을 채운다.
> 노드 키는 전 테이블 **node01~node08** 로 통일해야 통합이 깨지지 않는다.
