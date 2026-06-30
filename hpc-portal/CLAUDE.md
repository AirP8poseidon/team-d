# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> 이 파일은 `hpc-portal/` 앱의 **기술 가이드**다. 저장소 루트 `CLAUDE.md`(해커톤 운영 규칙 + 원본 청사진)도 함께 적용된다 — 그쪽 "현재 상태: 백엔드 없음"은 옛 내용이고, 백엔드는 여기 구현돼 있다. 충돌 시 실제 코드(이 디렉터리)가 기준.

## 무엇인가
사내 HPC 통합 포털 — SLURM 자원 숫자 위에 **사람의 맥락(누가·왜) + 채팅 + 운영 가시성(온도/디스크/NFS)** 을 얹는 단일 FastAPI + SQLite 웹앱. 프론트는 정적 HTML + 바닐라 `fetch` + 2~3초 폴링(WebSocket 없음). 한국어 UI.

## 명령어
```bash
cd hpc-portal
pip install -r requirements.txt
uvicorn main:app --reload --port 8000     # http://localhost:8000 · API 문서 /docs

pytest -q                                 # 전체 테스트
pytest tests/test_parsers.py -q           # 단일 파일
pytest tests/test_parsers.py::test_name   # 단일 테스트
```
의존성은 의도적으로 최소(`fastapi`, `uvicorn[standard]`, 테스트용 `pytest`/`httpx`)다. `sqlalchemy`/`jinja2`/`python-multipart`/`requests` 는 **쓰지 않는다** — raw `sqlite3`, JSON only, 정적 HTML+fetch. 재현성 위해 `pip freeze` 로 버전 핀.

## 데이터 흐름 — 이게 핵심 아키텍처
앱은 DB를 직접 채우지 않는다. **컬렉터 seam**을 통한다 (`main.py` → `collectors/` → `db.upsert_*`):

1. `main.py` lifespan startup: `init_db()` → `seed_if_empty()` → `run_collector_once()` 즉시 1회 적재 → `asyncio` 백그라운드 태스크가 **5초(`REFRESH_SECONDS`)마다** 컬렉터 재구동(blocking sqlite는 `asyncio.to_thread`로 격리).
2. 어떤 컬렉터를 쓸지는 **`COLLECTOR` 환경변수**가 결정 (`get_collector()` in `collectors/__init__.py`, 기본 `mock`):
   - `mock` — `data/sample_{sinfo,squeue,health}.txt` 파싱 (`collectors/mock.py`). 데모 기본값.
   - `ingest` — `data/incoming/<node>.json` 파일들을 읽음 (`collectors/ingest.py`). 실서버 push 경로.
   - `slurm` / `prometheus` — 스텁만 있음 (`collectors/{slurm,prometheus}.py`), 미구현 → mock 폴백.
   - 알 수 없는 이름 → mock 폴백.
3. 모든 컬렉터는 `Collector` ABC(`collectors/base.py`)를 구현: `collect_nodes/jobs/health()` 가 **DB 컬럼명과 1:1로 맞는 dict 리스트**를 반환. 새 데이터 소스 추가 = 이 ABC를 drop-in 구현 + `get_collector()`에 등록. **`main.py`·라우터·스키마 변경 불필요.**

### 절대 깨면 안 되는 계약
- **컬렉터는 어떤 입력에도 예외를 던지지 않는다** (결정 5A). 깨진 행/파일은 skip + 경고 로그만. 부팅이 멈추면 안 됨. `mock`/`ingest` 의 방어적 `_to_int`·가드 패턴을 따를 것.
- **노드 키는 전 테이블 통일** (`db.NODES`, 결정 T8). 기본 `node01`..`node08`. 모니터링·헬스·통계·`node_usage`·ingest 가 전부 같은 집합을 써야 조인이 성립. `ingest` 는 `db.NODES` 밖 노드를 **버린다**.
- **`init_db()`/`seed_if_empty()` 는 멱등** (결정 2A). `CREATE TABLE IF NOT EXISTS` + "비었을 때만" 시드. `seed_if_empty` 는 `usage_log`/`servers`/`posts` 만 시드하고 `nodes`/`jobs`/`node_health`(컬렉터가 채움)와 사용자 생성 데이터(`messages`/`node_usage`)는 **건드리지 않는다**.
- **DB 커넥션은 호출마다 새로 연다** (결정 1A, `db.get_db`): `check_same_thread=False` + WAL + `busy_timeout`. 라우터는 `Depends(db_dep)` 로 받고 자동 close. 커넥션을 모듈 전역에 캐시하지 말 것.

## 파일 소유 경계 (병렬 개발 — 본인 파일만 수정)
| 담당 | 라우터 / 정적 | DB 테이블 |
|---|---|---|
| **팀장(공통)** | `main.py`, `db.py`, `collectors/*`, `routers/monitoring.py`, `static/{monitoring,index}.html`, `static/{common.css,_nav.html,include.js}` | `nodes`, `jobs`, `node_usage` |
| **팀원1** | `routers/{wiki,chat}.py`, `static/wiki.html`, `static/chat-widget.js` | `servers`, `posts`, `messages` |
| **팀원2** | `routers/{stats,system}.py`, `static/{stats,system}.html`, `data/sample_health.txt` | `node_health`, `usage_log` |

공통 파일(`main.py`/`db.py`/`requirements.txt`/공통 static) 변경은 팀장 경유. 라우터는 자체 `/api/<area>` prefix 를 보유하고 **단독으로 `/docs` 에서 200 응답**해야 한다(통합 전제). 각 API 라우트 위치는 `routers/*.py` 의 `@router.get/post` 참고.

### 프론트 통합 규칙
- 네비는 자가주입: 각 페이지에 `<div id="nav-placeholder"></div>` + `<script src="/static/include.js"></script>` 한 줄 → `_nav.html` fetch + 현재 페이지 `.active`.
- 채팅은 페이지가 아니라 **위젯**(`chat-widget.js`, 팀원1 소유): `monitoring`/`wiki`/`stats`/`system` 4개 페이지가 `<script src="/static/chat-widget.js">` 한 줄로 띄움. `index` 제외.
- 팀원 페이지(`wiki/stats/system.html`)와 `monitoring.html` 은 현재 **헤더-only 스텁** — 각 파일 `TODO(팀원X)` 주석대로 `fetch` 배선을 채운다.
- 디자인 토큰(폰트·CSS 변수·네비)은 루트 `CLAUDE.md` 통합 규칙 절을 따른다.

## 실서버 수집 파이프라인 (`agent/`)
실 클러스터(RHEL7 CPU 클러스터, `master` + `node1`..`node13`)에서 자원 텔레메트리를 **읽기 전용**(sudo·설치 불필요)으로 모아 `ingest` 컬렉터에 먹이는 스크립트들. 포털과 클러스터가 망 격리돼 있어 전송 경로가 둘:
- `agent/node_report.py` (py3) — 노드가 자기 정보를 JSON으로 scp push → 포털 `data/incoming/`.
- `agent/scan_cluster.sh` — 한 호스트에서 전 노드 SSH 순회(pull) → `data/incoming/` 또는 `PORTAL_HOST` 로 scp.
- `agent/scan_push.sh` + `agent/collect_node.py` (py2.7 호환) — master에서 수집 → `data/live/*.json` 에 git commit/push. **망 격리(git만 연결) 시 git을 전송 매개로 사용.** 포털 쪽은 git pull 후 읽음.
- `agent/probe_server.sh` — 노드 제원 정찰(스펙 확인용), 결과는 `agent/probes/`.
- 노드 목록은 `HPC_NODES` 환경변수로 주입 (`db.NODES` 도 동일 변수를 읽음). 미설정 시 데모 기본 `node01..node08`.

`data/incoming/` 와 `data/live/` 는 `.gitkeep` 만 추적되는 런타임 수집 디렉터리다.

## 테스트
`tests/conftest.py` 가 `HPC_DB_PATH` 를 임시 파일로 강제해 `app.db` 를 건드리지 않는다. 커버리지: 파서 정상/깨진행(`test_parsers`), 멱등 시드(`test_seed_idempotent`), 노드키 정합(`test_node_keys`), 라우터 200 스모크(`test_smoke`).
