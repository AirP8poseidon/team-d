# 사내 HPC 통합 포털 — 개발 사양서 (SPEC)

| 항목 | 내용 |
|---|---|
| 프로젝트 | 사내 HPC 통합 포털 (HPC Portal) |
| 팀 | team-d |
| 문서 버전 | v1.0 (2026-06-30) |
| 작성 | LeeSeongHoo (팀장) |
| 상위 문서 | `00_plan/DEV_BLUEPRINT.md` (확정 스펙·단일 진실 공급원) |
| 본 문서 위상 | 블루프린트를 **정식 사양 형식**으로 구조화·구체화. 충돌 시 `DEV_BLUEPRINT.md`가 우선한다. |

---

## 1. 문서 개요

### 1.1 목적
SLURM 자원 숫자만으로는 알 수 없는 **사람의 맥락(누가·왜)**, **실시간 소통**, **운영 가시성(온도·스토리지)** 을 한 화면에 모은 사내 HPC 통합 포털을 개발하기 위한 기능·데이터·인터페이스·검수 기준을 정의한다.

### 1.2 범위
- 포함: FastAPI + SQLite 단일 웹앱, 정적 HTML/JS 프론트(페이지 5 + 채팅 위젯), 목업 데이터 기반 동작.
- 제외: 실 SLURM/시스템 서버 연동, 인증/권한, WebSocket 실시간, 외부 배포·운영.

### 1.3 용어
| 용어 | 정의 |
|---|---|
| 노드(node) | 계산 서버 1대. 명명은 `node01`~`node08`로 **고정**. |
| 작업 맥락(node_usage) | 특정 노드에서 "누가·무슨 목적으로·언제까지" 쓰는지의 사람 정보. |
| 스케줄러 작업 | SLURM `squeue` 또는 PBS `qstat`처럼 큐 시스템에 잡히는 작업. 이번 구현은 `sample_squeue.txt`만 자동 파싱한다. |
| 직접 실행 작업 | `mpirun` 직접 실행처럼 큐 샘플에 안 잡히는 작업. 이번 구현은 자동 탐지하지 않고 `node_usage` 폼으로 수동 등록한다. |
| 채팅 위젯 | 페이지가 아니라 모든 페이지에 떠 있는 플로팅 채팅창(`chat-widget.js`). |
| 폴링 | 2~3초 간격 `fetch` 재요청으로 갱신하는 의사-실시간 방식. |

### 1.4 참조
`DEV_BLUEPRINT.md`(§2 역할·§3 구조·§4 DB·§6 API·§7 통합·§8 빌드순서), `HPC포털_개발_핸드오버.md`(일반 원칙), 프로젝트 `CLAUDE.md`.

---

## 2. 시스템 개요

### 2.1 배경·문제
HPC 사용자들이 노드 사용 현황·서버 환경·노하우를 메신저/구두/개별 문의로 매번 확인·조율한다. 자원 가시성은 SLURM이 주지만 "누가 왜 쓰는지", "지금 물어볼 사람", "노드가 건강한지"는 흩어져 있다.

### 2.2 목표
한 포털에서 ① 자원+사람 맥락을 함께 보고, ② 어느 페이지서든 실시간으로 소통하며, ③ 온도·디스크·NFS 등 운영 상태까지 점검한다.

### 2.3 사용자
사내 HPC 사용 연구원·운영자(익명/사내 한정). 인증 없음(목업 단계).

---

## 3. 기능 요구사항 (FR)

> 우선순위: **M**(필수)·S(권장)·C(여유). 담당: 팀장/팀원1/팀원2.

### 3.1 모니터링 (팀장) — `monitoring.html`
| ID | 우선 | 요구사항 |
|---|---|---|
| FR-M1 | M | `node01~08`의 status·CPU·GPU·메모리 사용률을 카드로 표시. |
| FR-M2 | M | 노드별 GPU 사용률을 Chart.js 막대 차트로 시각화. |
| FR-M3 | M | 현재 작업 큐(job): 사용자·노드·목적·상태·경과시간 목록. 이번 구현은 `sample_squeue.txt` 기반이며 PBS는 향후 확장. |
| FR-M4 | M | 노드 카드에 **현재 작업 맥락(사용자/목적/예상시간/출처)** 표시 — `node_usage` 기반. |
| FR-M5 | M | 작업 맥락 등록 폼: `{node, user, purpose, eta, source?}` POST 후 즉시 반영. |
| FR-M6 | S | CPU/GPU/메모리 수치를 2~3초 폴링으로 갱신. |
| FR-M7 | M | `mpirun` 직접 실행 등 스케줄러 큐에 없는 작업은 `source=mpirun` 또는 `manual`로 수동 등록해 표시. |

### 3.2 정보공유 위키 (팀원1) — `wiki.html`
| ID | 우선 | 요구사항 |
|---|---|---|
| FR-W1 | M | 서버 환경 카드(이름·OS·스펙·모듈·SSH 접속법) 목록. |
| FR-W2 | M | 노하우 게시판: 글 목록 + 작성(제목·작성자·본문). |
| FR-W3 | M | 게시판 키워드 검색(`?q=`). |
| FR-W4 | S | 사용법 가이드 섹션(정적 콘텐츠). |

### 3.3 실시간 채팅 위젯 (팀원1) — `chat-widget.js`
| ID | 우선 | 요구사항 |
|---|---|---|
| FR-C1 | M | 숨김/열기 토글되는 플로팅 채팅창. 자체 CSS·로직을 스크립트가 주입. |
| FR-C2 | M | 메시지 전송 `{sender, body}` + 2~3초 `after=id` 증분 폴링 수신. |
| FR-C3 | M | `<script src="/static/chat-widget.js">` 한 줄로 임의 페이지에 탑재. |
| FR-C4 | M | `index` **제외**, `monitoring/wiki/stats/system` 4개 페이지에 노출. |

### 3.4 사용량 통계 (팀원2) — `stats.html`
| ID | 우선 | 요구사항 |
|---|---|---|
| FR-S1 | M | 노드별/사용자별 사용량 집계 표·차트. |
| FR-S2 | M | 사용량 추이(시간/일자) 라인 차트. |
| FR-S3 | C | 추가 아이디어 캐치올(이 페이지에 자유 확장). |

### 3.5 시스템 상태 (팀원2) — `system.html`
| ID | 우선 | 요구사항 |
|---|---|---|
| FR-Y1 | M | `node01~08`의 온도·디스크 상태·NFS 연결 상태 표시. |
| FR-Y2 | M | `data/sample_health.txt` 파싱 → `node_health` 적재 후 표출. |
| FR-Y3 | S | 임계값 초과 항목 색상 경고(디자인 토큰 red/orange). |

### 3.6 공통/랜딩 (팀장) — `index.html`, 네비
| ID | 우선 | 요구사항 |
|---|---|---|
| FR-G1 | M | 5개 페이지 상단 공통 네비(`홈/모니터링/정보공유/사용량 통계/시스템 상태`), 현재 페이지 `.active`. |
| FR-G2 | M | 랜딩(`index`)은 포털 소개. **채팅 위젯 미포함**. |

---

## 4. 비기능 요구사항 (NFR)

| ID | 분류 | 요구사항 |
|---|---|---|
| NFR-1 | 성능 | 단일 노트북에서 동작. API 응답 < 200ms(로컬·SQLite). 폴링 주기 2~3초. |
| NFR-2 | 호환 | Python 3.9+. 최신 크롬/엣지. UI 전부 한국어. |
| NFR-3 | 재현성 | `pip freeze`로 버전 핀 → `requirements.txt`. 다른 PC에서 `pip install -r` 후 동일 재현. |
| NFR-4 | 의존성 최소 | 백엔드 `fastapi`+`uvicorn`만. DB는 표준 `sqlite3`. 프론트 프레임워크 없음(바닐라 fetch + Chart.js CDN). |
| NFR-5 | 오프라인 대비 | CDN 차단 시 Chart.js 1파일을 `static/`에 내려받아 로컬 참조로 교체 가능. |
| NFR-6 | 보안 | 미공개 관측 원본·개인정보·대외비 좌표/수치 미사용. 목업/익명 데이터만. |
| NFR-7 | 독립성 | 각 API는 타인 코드 없이 `/docs`에서 단독 응답해야 함(통합 전제). |
| NFR-8 | 범위 통제 | `ps`, `nvidia-smi`, PBS `qstat` 실시간 파싱은 이번 구현 범위 밖. 필요 시 샘플 파일 기반 확장으로만 고려. |

---

## 5. 시스템 아키텍처

### 5.1 기술 스택
- 백엔드: Python **FastAPI** + 표준 `sqlite3`, ASGI 서버 `uvicorn[standard]`.
- 프론트: 정적 HTML/CSS/JS + `fetch()` + `setInterval` 폴링. 차트 Chart.js 4.4.1(CDN).
- 데이터: 실서버 연동 없음 — `data/`의 샘플 텍스트를 **앱 시작 시 1회 파싱**해 SQLite 적재.

### 5.2 폴더 구조 (소유자 표시 — 본인 파일만 수정)
```
hpc-portal/
├── main.py                 [팀장]  앱 진입점·라우터 5개 등록·정적 서빙
├── db.py                   [팀장]  SQLite 연결·테이블 초기화·시드
├── requirements.txt        [팀장]
├── data/
│   ├── sample_squeue.txt   [팀장]  job 목업
│   ├── sample_sinfo.txt    [팀장]  노드 목업
│   └── sample_health.txt   [팀원2] 온도/디스크/NFS 목업
├── routers/
│   ├── monitoring.py       [팀장]   /api/monitoring/*
│   ├── wiki.py             [팀원1]  /api/wiki/*
│   ├── chat.py             [팀원1]  /api/chat/*
│   ├── stats.py            [팀원2]  /api/stats/*
│   └── system.py           [팀원2]  /api/system/*
└── static/
    ├── common.css          [팀장]  공통 디자인 토큰
    ├── _nav.html           [팀장]  공통 네비 스니펫
    ├── chat-widget.js      [팀원1] 플로팅 채팅(자체 주입)
    ├── index.html          [팀장]  랜딩(위젯 미포함)
    ├── monitoring.html     [팀장]  + chat-widget
    ├── wiki.html           [팀원1] + chat-widget
    ├── stats.html          [팀원2] + chat-widget
    └── system.html         [팀원2] + chat-widget
```
> 공통 파일(`main.py`/`db.py`/`common.css`/`_nav.html`/`index.html`/`requirements.txt`)은 **팀장만** 수정. 팀원 라우터는 팀장이 `main.py`에 한 줄 등록.

---

## 6. 데이터 설계 (DB 스키마)

> 소유자별로 테이블이 분리되어 동시 수정 충돌이 없다.

```sql
-- [팀장] 모니터링
nodes(
  node TEXT PRIMARY KEY,
  status TEXT NOT NULL,
  cpu INTEGER NOT NULL,
  gpu INTEGER NOT NULL,
  mem INTEGER NOT NULL,
  gpu_model TEXT
)
jobs(
  job_id TEXT PRIMARY KEY,
  user TEXT NOT NULL,
  node TEXT NOT NULL,
  purpose TEXT,
  status TEXT NOT NULL,
  elapsed TEXT
)
node_usage(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  node TEXT NOT NULL,
  user TEXT NOT NULL,
  purpose TEXT NOT NULL,
  eta TEXT,
  source TEXT NOT NULL DEFAULT 'manual',
  created_at TEXT NOT NULL
)

-- [팀원1] 위키 + 채팅
servers(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, os TEXT, spec TEXT, modules TEXT, ssh TEXT)
posts(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, author TEXT NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL)
messages(id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL)

-- [팀원2] 통계 + 시스템 상태
node_health(node TEXT PRIMARY KEY, temp INTEGER NOT NULL, disk_status TEXT NOT NULL, nfs_status TEXT NOT NULL, updated_at TEXT NOT NULL)
usage_log(id INTEGER PRIMARY KEY AUTOINCREMENT, node TEXT NOT NULL, user TEXT NOT NULL, gpu_hours REAL NOT NULL, day TEXT NOT NULL)
```
- `node` 값은 전 테이블 `node01`~`node08` 표기로 통일(통합 키).
- 시간 저장은 ISO 문자열, 화면 표기는 `"HH:MM"`.
- `node_usage.source` 값 예: `manual`, `mpirun`, `slurm`, `pbs`. 이번 구현에서 `slurm/pbs` 자동 변환은 필수가 아니며, 직접 실행 작업 구분용으로 주로 사용한다.

### 6.1 데이터 소스(목업) 적재
| 파일 | → 테이블 | 비고 |
|---|---|---|
| `data/sample_squeue.txt` | `jobs` | SLURM `squeue` 유사 출력 파싱 |
| `data/sample_sinfo.txt` | `nodes` | SLURM `sinfo` 유사 출력 파싱 |
| `data/sample_health.txt` | `node_health` | 온도/디스크/NFS 목업 |
| (자체 시드) | `usage_log`, `servers`, `posts` 초기값 | `db.py` 시드 |

### 6.2 샘플 파일 포맷 예시
파서는 아래처럼 공백 구분 텍스트를 기준으로 단순 구현한다. 실제 서버 출력과 완전 일치할 필요는 없다.

`data/sample_squeue.txt`
```text
JOBID USER NODE PURPOSE STATUS ELAPSED
101 kim node04 deep-learning RUNNING 02:10
102 lee node02 wrf-test PENDING 00:00
```

`data/sample_sinfo.txt`
```text
NODE STATUS CPU GPU MEM GPU_MODEL
node01 idle 12 0 22 A100
node04 alloc 84 91 76 A100
```

`data/sample_health.txt`
```text
NODE TEMP DISK_STATUS NFS_STATUS UPDATED_AT
node01 42 ok ok 2026-06-30T14:00:00
node04 71 warning ok 2026-06-30T14:00:00
```

`mpirun` 직접 실행 작업은 위 샘플 파일에서 자동 탐지하지 않는다. 사용자가 모니터링 페이지의 `node_usage` 폼에 `source=mpirun`으로 등록한다.

---

## 7. API 사양

> 공통: JSON 요청/응답. 해커톤 구현 단순화를 위해 성공은 모두 200, 검증 실패 422(pydantic), 미존재 404. base는 `/api`.

### 7.1 모니터링 (팀장)
| 메서드·경로 | 요청 | 응답(예) |
|---|---|---|
| `GET /api/monitoring/nodes` | — | `[{node, status, cpu, gpu, mem, gpu_model}]` |
| `GET /api/monitoring/jobs` | — | `[{job_id, user, node, purpose, status, elapsed}]` |
| `GET /api/monitoring/usage` | — | `[{id, node, user, purpose, eta, created_at}]` |
| `POST /api/monitoring/usage` | `{node, user, purpose, eta, source?}` | `{id, node, user, purpose, eta, source, created_at}` |

### 7.2 위키 (팀원1)
| 메서드·경로 | 요청 | 응답(예) |
|---|---|---|
| `GET /api/wiki/servers` | — | `[{id, name, os, spec, modules, ssh}]` |
| `GET /api/wiki/posts?q=검색어` | 쿼리 `q`(선택) | `[{id, title, author, body, created_at}]` |
| `POST /api/wiki/posts` | `{title, author, body}` | `{id, ...저장값}` |

### 7.3 채팅 (팀원1)
| 메서드·경로 | 요청 | 응답(예) |
|---|---|---|
| `GET /api/chat/messages?after=id` | 쿼리 `after`(선택, 증분) | `[{id, sender, body, created_at}]` |
| `POST /api/chat/messages` | `{sender, body}` | `{id, ...저장값}` |

### 7.4 통계·시스템 (팀원2)
| 메서드·경로 | 요청 | 응답(예) |
|---|---|---|
| `GET /api/stats/usage` | — | `{by_node:[{node, gpu_hours}], by_user:[{user, gpu_hours}], trend:[{day, gpu_hours}]}` |
| `GET /api/system/health` | — | `[{node, temp, disk_status, nfs_status, updated_at}]` |

---

## 8. UI/UX 사양 (디자인 토큰 — 모든 페이지 동일)

- `<html lang="ko">`, 폰트 `"Malgun Gothic","Apple SD Gothic Neo",Arial,sans-serif`.
- CSS 변수: `--bg:#f4f6fb; --paper:#fff; --ink:#172033; --muted:#64748b; --line:#d8dee9; --blue:#1d4ed8; --navy:#0f172a; --green:#047857; --orange:#b45309; --red:#b91c1c`.
- 상단 네비: 네이비 배경, 좌측 "사내 HPC 포털", 우측 5링크(`홈/모니터링/정보공유/사용량 통계/시스템 상태` → `index/monitoring/wiki/stats/system`), 현재 페이지 `.active` 강조.
- 상태 색상: 정상 green, 주의 orange, 위험 red, 강조 blue.
- 시간 표기: 화면 `"HH:MM"`, 저장 ISO.

---

## 9. 통합 사양 (통합 접점 — 모두 `node01~08` 키로 연결)

| # | 접점 | 소유 | 내용 |
|---|---|---|---|
| 1 | node_usage → 모니터링 카드 | 팀장 | 노드 카드에 현재 작업 목적/사용자/예상시간/출처 + 등록 폼. `mpirun` 직접 실행은 이 폼으로 수동 등록. |
| 2 | chat-widget 주입 | 팀원1 | 4개 페이지가 `<script src="/static/chat-widget.js">` 한 줄 추가. |
| 3 | system/health 노드 정합 | 팀원2 | `node01~08`로 모니터링과 동일 노드 식별. |
| 4 | stats 집계 | 팀원2 | `usage_log`(자체 시드) 기반. 필요 시 `/api/monitoring/jobs`를 GET으로만 보강(쓰기 충돌 없음). |

> 통합 = "파일을 한 폴더에 모으기 + 위젯 스크립트 한 줄 + 노드 키 정합 확인"이 전부.

---

## 10. 개발·빌드 계획

### 10.1 역할 분담
| 담당 | 페이지/기능 |
|---|---|
| 팀장 | 공통 뼈대 + `index` + `monitoring`(+ node_usage) + 막판 통합 |
| 팀원1 | `wiki` + `chat-widget` |
| 팀원2 | `stats` + `system` |

### 10.2 빌드 순서 (철칙: 1단계 공유 전 본문 개발 금지)
1. **공통 뼈대(팀장 최우선 공유)**: `main.py`+`db.py`+`requirements.txt`, `common.css`+`_nav.html`, 빈 5페이지, 빈 라우터 5개 등록 → **공유 시점이 병렬 시작 신호.**
2. **병렬 개발(각자 자기 파일만)**: 목업을 `static/`으로 이전 + `fetch` 배선.
3. **통합(팀장)**: 5페이지 한 폴더 + 네비 점검 + 위젯 주입 확인 + 노드 키 정합 스모크 테스트.

### 10.3 실행
```bash
pip install fastapi "uvicorn[standard]"
pip freeze | grep -iE '^(fastapi|uvicorn|starlette|pydantic|anyio|click|h11)=' > requirements.txt
uvicorn main:app --reload --port 8000   # http://localhost:8000 · /docs
```

---

## 11. 시험·검수 기준 (인수 조건)

### 11.1 단위(각자)
- [ ] 본인 API가 `/docs`에서 단독 200 응답.
- [ ] 응답이 §7 스키마와 일치, `node` 값은 `node01~08`.
- [ ] 본인 페이지가 §8 디자인 토큰 준수.

### 11.2 통합
- [ ] 서버 하나로 5페이지 네비 이동 정상.
- [ ] 채팅 위젯이 4개 페이지(index 제외)에 뜨고 폴링 송수신.
- [ ] `node_usage` 등록 → 모니터링 카드 즉시 반영.
- [ ] `system/health`·`stats` 노드 표기가 모니터링과 정합.

### 11.3 시연 시나리오 (한 흐름)
1. 채팅 위젯으로 "node04 딥러닝 시작합니다, ~18시" 소통.
2. 모니터링: node04에 작업 맥락(`mpirun 딥러닝`/사용자/~18시/source=mpirun)을 등록하면 카드에 즉시 반영 + CPU/GPU.
3. 사용량 통계: 노드별 GPU 점유 추이·사용자별 집계.
4. 시스템 상태: node04 온도·디스크·NFS 정상 확인.
5. 위키: sbatch 사용법 확인.
> 메시지: "SLURM은 자원 숫자를, 우리 포털은 **사람의 맥락 + 실시간 소통 + 운영 가시성**을 더한다."

---

## 12. 제약·가정·리스크
- 제약: 실서버 미연동(목업), 인증 없음, WebSocket 미사용(폴링).
- 가정: 노드는 8대 고정(`node01~08`), 단일 호스트 로컬 실행.
- 리스크 & 대응:
  - CDN 차단 → Chart.js 로컬 동봉(NFR-5).
  - 공통 파일 동시 수정 → 팀장 단독 수정 규칙(§5.2).
  - 노드 표기 불일치 → 전 테이블 `node01~08` 강제(§6, §9).
  - `mpirun` 직접 실행 작업 누락 → 자동 탐지 대신 `node_usage.source=mpirun` 수동 등록으로 시연 범위 내 해결.
  - 세션 단절(1.5일) → `/context-save`·`/context-restore`로 맥락 복구.

---

## 13. 엔지니어링 검토 반영 (잠금 결정 — 코딩 전 필수)

> `/plan-eng-review`(2026-06-30)에서 합의·잠근 결정. **이 6건은 구현 시 반드시 반영**한다. 5건이 팀장 공통 뼈대(`db.py`/`static`)에 모이므로, §8-1 공통 뼈대 공유 전에 1A·2A·4A·5A를 박아 둔다.

| # | 우선 | 결정 | 소유 |
|---|---|---|---|
| 1A | P1 | **`db.py` 동시성 표준**: 요청별 connection 열고닫기 + `check_same_thread=False` + `PRAGMA journal_mode=WAL` + `PRAGMA busy_timeout=5000`을 공통 helper(`get_db()`)에 1회 설정. 팀원은 `get_db()`만 사용. | 팀장 |
| 2A | P1 | **멱등 초기화**: `CREATE TABLE IF NOT EXISTS` + 시드는 "테이블이 비었을 때만"(SELECT COUNT 또는 `INSERT OR IGNORE/REPLACE`). `--reload` 재부팅에 안전, 사용자 데이터 보존. | 팀장 |
| 3A | P2 | **node_usage 최신 1건 표시**: 모니터링 카드는 노드별 `ORDER BY created_at DESC LIMIT 1`로 현재 작업 맥락 1건만 표시(스키마 변경 없음). | 팀장 |
| 4A | P2 | **JS 인클루드 네비**: `_nav.html`을 페이지당 부트스트랩 스니펫 한 줄로 `fetch` 주입 + `location.pathname`으로 `.active` 자동 설정. nav 마크업 1곳(채팅 위젯과 동일 자가주입 패턴). | 팀장 |
| 5A | P1 | **파서 입력 가드**: `sample_*.txt` 파싱 시 헤더/빈 줄 skip, 칸 수 검증, `int()` try/except. 잘못된 행은 건너뛰고 로그만 → 어떤 입력에도 **부팅 무중단**. | 팀장(squeue/sinfo)·팀원2(health) |
| 6A | P2 | **pytest 최소 세트**: (1)파서 정상/깨진행 (2)멱등 시드 2회 init→행수 동일 (3)`node01~08` 전 테이블 정합 (4)각 라우터 `TestClient` 200 스모크. | 각자 |

**추가 작업(검토 파생):**
- T7 (P3): `GET /api/chat/messages` 초기 로드 `LIMIT`(최근 50건) — 무한 증가 방지. (팀원1)
- T8 (P2): 노드 키 공유 기준 `NODES = node01..node08` 상수화 + 6A의 정합 테스트로 강제. (팀장 시드 기준 / tests)

**통합 실패 모드(검토):** 노드 키 불일치는 테스트·에러처리가 없으면 *조용히* 모니터링↔시스템상태가 어긋난다 → 6A의 정합 테스트가 유일한 안전망(critical gap 해소).

**보류(NOT in scope):** `node_usage` 활성/해제 상태(3B), 실서버 `ps`/`nvidia-smi`/PBS 실시간 파싱, 풀 테스트 커버리지(6C). 모두 향후 확장.
