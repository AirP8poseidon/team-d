# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> 상위 폴더의 `team-d/CLAUDE.md`는 **해커톤 운영 규칙**(제출·로그·채점)이고 자동 로드된다. 이 파일은 그 아래에서 작업할 때 함께 로드되는 **HPC 포털 프로젝트의 기술 문서**다. 둘 다 적용된다.

## 단일 진실 공급원 (먼저 읽을 것)
`00_plan/DEV_BLUEPRINT.md` 가 이 프로젝트의 **확정 스펙**이다. 역할·페이지·소유 파일·DB·API 구성은 이 문서가 기준이며, 더 오래된 `HPC포털_개발_핸드오버.md`의 같은 항목을 **대체**한다(핸드오버는 일반 원칙만 유효). 아래 요약과 충돌하면 `DEV_BLUEPRINT.md`가 우선한다. 새 작업 전 §2(역할)·§4(DB)·§6(API)·§7(통합 접점)을 확인하라.

## 무엇을 만드는가
사내 HPC 통합 포털 — SLURM 자원 숫자 위에 **사람의 맥락(누가·왜) + 실시간 소통 + 운영 가시성(온도·스토리지)** 을 얹는 웹앱. 페이지 5개 + 플로팅 채팅 위젯을 **3명이 나눠 독립 개발 후 통합**한다.

## 확정된 기술 결정 (변경 금지)
- **백엔드**: Python **FastAPI + SQLite** 단일 앱. 프론트는 정적 HTML/JS + 바닐라 `fetch`(프레임워크 없음).
- **구현 방식(B안)**: 기존 HTML 목업을 `static/`으로 옮겨 **가짜 데이터만 `fetch`로 교체**(새로 그리지 않고 재사용·배선).
- **실시간성**: WebSocket 안 씀. **2~3초 폴링**으로 채팅·현황 갱신.
- **데이터 소스**: 실서버 연동 없음. `data/`의 샘플 텍스트(squeue/sinfo/health)를 **앱 시작 시 1회 파싱**해 SQLite에 적재.
- **언어**: 한국어 UI. 차트는 Chart.js 4.4.1 (CDN).

## 아키텍처의 핵심 — 충돌 없는 병렬 개발
세 사람이 **같은 파일을 절대 동시에 만지지 않도록** 경계가 설계돼 있다. 각자 자기 라우터 + 자기 페이지 + 자기 DB 테이블만 건드린다.

| 담당 | 소유 파일 | DB 테이블 | API |
|---|---|---|---|
| **팀장** | `routers/monitoring.py`, `static/monitoring.html`, `data/sample_squeue.txt`·`sample_sinfo.txt` | `nodes`, `jobs`, `node_usage` | `GET /api/monitoring/nodes`·`/jobs`·`/usage`, `POST /api/monitoring/usage` |
| **팀원1** | `routers/wiki.py`, `routers/chat.py`, `static/wiki.html`, `static/chat-widget.js` | `servers`, `posts`, `messages` | `GET /api/wiki/servers`·`/posts?q=`, `POST /api/wiki/posts`, `GET /api/chat/messages?after=`, `POST /api/chat/messages` |
| **팀원2** | `routers/stats.py`, `routers/system.py`, `static/stats.html`, `static/system.html`, `data/sample_health.txt` | `node_health`, `usage_log` | `GET /api/stats/usage`, `GET /api/system/health` |

**공통 파일은 팀장만 수정**: `main.py`(앱 진입점·라우터 5개 등록·정적 서빙), `db.py`(연결·테이블 초기화·시드), `requirements.txt`, `static/common.css`, `static/_nav.html`, `static/index.html`. 팀원은 자기 라우터를 `main.py`에 등록만 팀장에게 요청한다.

## 통합 규칙 (지키지 않으면 통합이 깨짐)
- **노드 명명은 반드시 `node01`~`node08`.** 모니터링·시스템상태·통계·`node_usage`가 모두 이 표기를 써야 연결된다.
- **채팅은 페이지가 아니라 위젯**: `chat-widget.js`(팀원1 소유)가 자체 CSS·폴링을 주입하는 숨김/열기 플로팅 창. `index` **제외**, `monitoring`/`wiki`/`stats`/`system` 4개 페이지가 `<script src="/static/chat-widget.js"></script>` **한 줄**로 띄운다.
- **node_usage → 모니터링 카드**: 노드 카드에 "현재 작업 목적/사용자/예상시간" 표시 + 등록 폼(팀장 자기 파일 내에서 완결).
- **디자인 토큰 공통**(모든 페이지 동일): `<html lang="ko">`, 폰트 `"Malgun Gothic","Apple SD Gothic Neo",Arial,sans-serif`, CSS 변수 `--bg:#f4f6fb --paper:#fff --ink:#172033 --muted:#64748b --line:#d8dee9 --blue:#1d4ed8 --navy:#0f172a --green:#047857 --orange:#b45309 --red:#b91c1c`. 상단 네비는 네이비 배경 + 우측 링크 `홈/모니터링/정보공유/사용량 통계/시스템 상태`(→ `index/monitoring/wiki/stats/system`), 현재 페이지 `.active` 강조.
- **시간 표기**: 화면용 `"HH:MM"`, 저장은 ISO 문자열.

## 현재 상태 (중요)
- 아직 **백엔드(FastAPI/SQLite)가 없다.** `DEV_BLUEPRINT.md` §3 구조(`main.py`/`db.py`/`routers/`/`static/`/`data/`)는 생성 전이다. 빌드 순서는 §8: **팀장이 공통 뼈대(빈 5페이지 + 빈 라우터 5개 등록)를 먼저 공유 → 그 시점이 병렬 시작 신호.**
- 존재하는 것은 **정적 HTML 목업뿐**(API 연동 없는 디자인 프로토타입): `dev_part/{index,monitoring}.html`(팀장), `userA_part/wiki.html`(팀원1), `userB_part/chat.html`(팀원2 목업 → 본 개발 시 팀원1의 `chat-widget.js`로 흡수). 본 개발 시 `static/`로 옮겨 `fetch` 배선한다.
- `monitoring.html`은 Chart.js를 CDN으로 로드한다.

## 실행
```bash
pip install fastapi "uvicorn[standard]"   # requirements.txt 생성 후엔 pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# http://localhost:8000  ·  API 문서 /docs 에서 각 라우터 단독 응답 확인
```
- DB는 표준 `sqlite3`(설치 불필요). `python-multipart`/`jinja2`/`sqlalchemy`/`httpx`는 **쓰지 않는다**(JSON만, 정적 HTML+fetch, raw sqlite3, 서버 간 호출 없음).
- 재현성(채점 ②): 설치 후 `pip freeze`로 버전을 핀해 `requirements.txt`에 고정한다.

## 작업 시 주의
- 자기 소유 파일만 수정하라. 공통 파일(`main.py` 등) 변경이 필요하면 팀장 경유.
- 각 API는 다른 사람 코드 없이 **단독으로 `/docs`에서 응답**해야 한다(통합 전제).
- 의미 있는 단계마다 상위 규칙대로 `submit/PROCESS_LOG.md`에 기록을 남긴다.
