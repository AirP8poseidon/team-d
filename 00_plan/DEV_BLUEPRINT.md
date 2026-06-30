# 사내 HPC 포털 — 개발 청사진 (DEV BLUEPRINT, 수정판)

> **이 문서의 위상**: `HPC포털_개발_핸드오버.md`는 초기 3분담(모니터링/위키/채팅) 전제였다. 인터뷰를 거쳐 **역할·페이지 구성을 개편**했으며, **역할·페이지·소유 파일·DB·API 구성은 이 문서가 핸드오버를 대체**한다. (핸드오버의 기술 결정 §2, 디자인 토큰 §4-2, 타임라인 §5 등 일반 원칙은 그대로 유효.)
>
> 새 세션은 이 문서 하나로 바로 착수할 수 있다.

---

## 0. 한 줄 요약

SLURM 자원 숫자 위에 **사람의 맥락(누가·왜) + 실시간 소통 + 운영 가시성(온도·스토리지)** 을 얹은 사내 HPC 통합 포털을, **FastAPI + SQLite 경량 풀스택**으로, **3명이 페이지를 나눠 독립 개발 후 통합**한다. 데이터는 SLURM/시스템 샘플 출력 **목업**으로 시작한다.

---

## 1. 확정된 기술 결정 (변경 금지)

- **백엔드**: Python **FastAPI + SQLite** 단일 앱. 프론트는 정적 HTML/JS.
- **구현 방식(B안)**: 기존 HTML 목업(`dev_part`/`userA_part`/`userB_part`)을 `static/`으로 옮겨 **가짜 데이터만 `fetch`로 교체**. 새로 그리지 않고 재사용 + 배선.
- **실시간성**: WebSocket 안 씀. **2~3초 폴링**으로 채팅 갱신.
- **데이터 소스**: 실서버 연동 없음. `data/`의 샘플 텍스트(squeue/sinfo/health)를 **시작 시 1회 파싱**해 SQLite 적재. `mpirun` 직접 실행처럼 스케줄러 큐에 안 잡히는 작업은 `node_usage` 수동 등록으로 표시한다.
- **언어**: 한국어 UI. 디자인 토큰은 §5.

> 왜 목업만으로 안 되나: 이 제품의 하이라이트는 "작업 맥락 등록 → 모니터링에 즉시 반영" 같은 **라이브 데이터 흐름**이다. 공유 상태(DB) 없이는 위조밖에 안 되며, 채점의 동작 완성도·업무 임팩트(27점)를 스스로 포기하게 된다.

---

## 2. 역할·페이지 구성 (개편 핵심)

| 담당 | 페이지 | 핵심 내용 |
|---|---|---|
| **팀장** | `index.html` | 랜딩 (**채팅 위젯 미포함**) |
| **팀장** | `monitoring.html` | CPU/GPU/메모리 모니터링 + **노드별 "현재 작업 맥락"(누가·왜)** 표시·등록. SLURM/PBS 밖의 `mpirun` 직접 실행도 수동 등록으로 커버 |
| **팀원1** | `wiki.html` (정보공유) | 서버 환경 카드 · 사용법 가이드 · 노하우 게시판(검색) |
| **팀원1** | **채팅 플로팅 위젯** | 별도 페이지 아님. **숨김/열기 토글**되는 떠 있는 채팅창 (`chat-widget.js`) |
| **팀원2** | `stats.html` (사용량 통계) | 노드별/사용자별 사용량 집계·추이 차트. **추가 아이디어 캐치올** |
| **팀원2** | `system.html` (시스템 상태) | **온도·디스크·NFS 연결** 등 CPU/GPU 외 점검 정보 |

**네비게이션**: `홈 / 모니터링 / 정보공유 / 사용량 통계 / 시스템 상태` → `index / monitoring / wiki / stats / system`.html. 현재 페이지 `.active` 강조. (채팅은 위젯이라 네비에 없음.)

**채팅 위젯 노출 규칙**: `index` **제외**, `monitoring`/`wiki`/`stats`/`system` 4개 페이지에 공유 표시.

---

## 3. 폴더/파일 구조 (소유자 표시 — 본인 파일만 수정)

```
hpc-portal/
├── main.py                 [팀장]  앱 진입점·라우터 5개 등록·정적 서빙
├── db.py                   [팀장]  SQLite 연결·테이블 초기화·시드
├── requirements.txt        [팀장]  fastapi, uvicorn
├── data/
│   ├── sample_squeue.txt   [팀장]  job 목업
│   ├── sample_sinfo.txt    [팀장]  노드 목업
│   └── sample_health.txt   [팀원2] 온도/디스크/NFS 목업
├── routers/
│   ├── monitoring.py       [팀장]  /api/monitoring/*  (nodes, jobs, usage)
│   ├── wiki.py             [팀원1] /api/wiki/*
│   ├── chat.py             [팀원1] /api/chat/*
│   ├── stats.py            [팀원2] /api/stats/*
│   └── system.py           [팀원2] /api/system/*
└── static/
    ├── common.css          [팀장]  공통 테마(디자인 토큰)
    ├── _nav.html           [팀장]  공통 상단 네비 스니펫
    ├── chat-widget.js      [팀원1] ★ 자체 주입 플로팅 채팅(CSS 인라인 가능)
    ├── index.html          [팀장]  랜딩 (채팅 위젯 미포함)
    ├── monitoring.html     [팀장]  + chat-widget
    ├── wiki.html           [팀원1] + chat-widget
    ├── stats.html          [팀원2] + chat-widget
    └── system.html         [팀원2] + chat-widget
```

> 공통 파일(`main.py`/`db.py`/`common.css`/`_nav.html`)은 **팀장만** 수정. 팀원 라우터는 팀장이 `main.py`에 한 줄 등록.

---

## 4. DB 테이블 (소유자별, 서로 안 겹침)

```sql
-- [팀장] 모니터링
nodes(node TEXT PK, status, cpu INT, gpu INT, mem INT, gpu_model)
jobs(job_id TEXT PK, user, node, purpose, status, elapsed)
node_usage(id PK, node, user, purpose, eta, source, created_at) -- "누가·왜" 맥락. source 예: manual/mpirun/slurm/pbs

-- [팀원1] 위키 + 채팅
servers(id PK, name, os, spec, modules, ssh)
posts(id PK, title, author, body, created_at)
messages(id PK, sender, body, created_at)

-- [팀원2] 통계 + 시스템 상태
node_health(node PK, temp, disk_status, nfs_status, updated_at) -- node01~08
usage_log(id PK, node, user, gpu_hours, day)                    -- 집계 시드(독립성 위해 자체 보유)
```

---

## 5. 공통 규칙 (디자인 토큰 — 모든 페이지 동일)

- `<html lang="ko">`, 폰트 `"Malgun Gothic","Apple SD Gothic Neo",Arial,sans-serif`
- 색상 변수: `--bg:#f4f6fb; --paper:#fff; --ink:#172033; --muted:#64748b; --line:#d8dee9; --blue:#1d4ed8; --navy:#0f172a; --green:#047857; --orange:#b45309; --red:#b91c1c`
- 상단 네비: 네이비 배경, 좌측 "사내 HPC 포털", 우측 5링크, 현재 페이지 강조.
- **노드 명명 규칙(통합 필수)**: `node01`~`node08`. 모니터링·시스템상태·통계·node_usage 모두 이 표기를 써야 연결됨.
- 시간 표기: 화면용 `"HH:MM"`, 저장은 ISO 문자열.

---

## 6. API 엔드포인트 (소유자별)

```
[팀장]   GET  /api/monitoring/nodes         노드 상태·자원
         GET  /api/monitoring/jobs          job 큐(사용자·목적)
         GET  /api/monitoring/usage         현재 작업 맥락 목록
         POST /api/monitoring/usage         맥락 등록 {node, user, purpose, eta, source?}

[팀원1]  GET  /api/wiki/servers
         GET  /api/wiki/posts?q=검색어
         POST /api/wiki/posts               {title, author, body}
         GET  /api/chat/messages?after=id   신규 메시지(폴링)
         POST /api/chat/messages            {sender, body}

[팀원2]  GET  /api/stats/usage              사용량 집계(노드별/사용자별/추이)
         GET  /api/system/health           노드별 온도·디스크·NFS 상태
```

---

## 7. 통합 접점 (4개 — 모두 `node01~08` 키로 연결)

1. **node_usage → 모니터링 카드** (팀장 단독, 자기 파일 내): 노드 카드에 "현재 작업 목적/사용자/예상시간/출처" 표시 + 등록 폼. `mpirun` 직접 실행 작업은 여기서 `source=mpirun` 또는 `manual`로 등록한다.
2. **chat-widget 주입** (팀원1 소유): 팀장·팀원2 페이지는 `<script src="/static/chat-widget.js"></script>` 한 줄만 추가.
3. **system/health 노드 정합** (팀원2): `node01~08`로 모니터링과 같은 노드 식별.
4. **stats 집계** (팀원2): `usage_log`(자체 시드) 기반. 필요 시 `/api/monitoring/jobs`를 GET으로만 읽어 보강(쓰기 충돌 없음).

> 통합은 사실상 "파일을 한 폴더에 모으기 + 위젯 스크립트 한 줄 + 노드 키 정합 확인"이 전부.

---

## 8. 빌드 순서 (핸드오버 §5 타임라인 매핑)

1. **공통 뼈대(팀장, 최우선 공유)**: `main.py`+`db.py`+`requirements.txt`, `common.css`+`_nav.html`, 빈 5페이지, `routers/` 5개 빈 라우터 등록. → **공유 시점이 병렬 시작 신호.**
2. **병렬 개발** (각자 자기 파일만): 목업을 `static/`으로 이전해 `fetch` 배선.
   - 팀장: squeue/sinfo 파싱 → nodes/jobs 적재 → 모니터링 화면 + node_usage 등록/표시. 스케줄러 미사용(`mpirun` 직접 실행 등)은 자동 탐지하지 않고 node_usage 폼으로 수동 등록.
   - 팀원1: 위키 CRUD + `chat-widget.js`(2~3초 폴링, 플로팅 토글).
   - 팀원2: `sample_health.txt`→node_health + 시스템 상태 화면, usage_log 시드→통계 차트.
3. **통합(팀장)**: 5페이지 한 폴더 + 네비 점검 + chat-widget 주입 확인 + 노드 키 정합 스모크 테스트.

> 철칙: 1단계(공통 뼈대 공유) 전에는 본문 개발 시작 금지. 뼈대는 "헤더+빈 틀" 수준이면 충분.

---

## 9. 시연 시나리오 (한 흐름)

1. 어느 페이지서든 **플로팅 채팅**으로 "node04 딥러닝 시작합니다, ~18시" 소통.
2. **모니터링**: node04에 `mpirun 딥러닝/김/~18시/source=mpirun` 작업 맥락을 등록하면 카드에 즉시 반영 + CPU/GPU 사용률 표시.
3. **사용량 통계**: 노드별 GPU 점유 추이·사용자별 사용량 집계.
4. **시스템 상태**: node04 온도·디스크·NFS 정상 확인.
5. **위키**: gpu-cluster sbatch 사용법 확인.

→ 메시지: "SLURM은 자원 숫자를, 우리 포털은 **사람의 맥락 + 실시간 소통 + 운영 가시성**을 더한다."

---

## 10. 새 세션 킥오프 프롬프트

### (A) 팀장 — 공통 뼈대 + 모니터링
```
나는 HPC 포털 팀장이야. 첨부한 DEV_BLUEPRINT.md(§3 파일구조·§4 DB·§6 API)를 그대로 따른다.
먼저 공통 뼈대만 만들어줘: FastAPI(main.py), SQLite 초기화(db.py), requirements.txt,
common.css·_nav.html(§5 디자인 토큰), 빈 5페이지(index/monitoring/wiki/stats/system, 헤더만),
routers/ 5개 빈 라우터 + main.py 등록.
이어서 모니터링(routers/monitoring.py + monitoring.html)을 §2 팀장 항목대로 개발.
data/sample_squeue·sinfo 파싱 → nodes/jobs 적재, node_usage 등록/표시까지.
mpirun 직접 실행처럼 squeue/PBS 큐에 안 잡히는 작업은 자동 탐지하지 말고 node_usage 폼에서 source=mpirun으로 수동 등록 가능하게 해.
기존 dev_part/monitoring.html 목업을 static/으로 재사용하고 fetch만 배선해.
```

### (B) 팀원1 — 위키 + 채팅 위젯
```
나는 HPC 포털 팀원1, 정보공유(위키)와 실시간 채팅 담당이야. DEV_BLUEPRINT.md를 따른다.
내 소유 파일은 routers/wiki.py, routers/chat.py, static/wiki.html, static/chat-widget.js 뿐(공통 파일 X).
§4의 servers/posts/messages 테이블, §6의 /api/wiki/*·/api/chat/* 엔드포인트대로:
- 위키: 서버 환경 카드 + 사용법 가이드 + 검색되는 노하우 게시판 (userA_part/wiki.html 재사용)
- 채팅: 숨김/열기 토글되는 자체 주입 플로팅 위젯(chat-widget.js), 2~3초 after 폴링.
  다른 페이지는 <script src="/static/chat-widget.js"> 한 줄로 띄울 수 있게 만들어.
디자인은 §5 준수.
```

### (C) 팀원2 — 사용량 통계 + 시스템 상태
```
나는 HPC 포털 팀원2, 사용량 통계와 시스템 상태 페이지 담당이야. DEV_BLUEPRINT.md를 따른다.
내 소유 파일은 routers/stats.py, routers/system.py, static/stats.html, static/system.html,
data/sample_health.txt 뿐(공통 파일 X).
§4의 node_health/usage_log 테이블, §6의 /api/stats/*·/api/system/* 엔드포인트대로:
- 사용량 통계: 노드별/사용자별 사용량 집계·추이 차트
- 시스템 상태: 노드별 온도·디스크·NFS 연결 상태 (sample_health.txt 파싱)
node 값은 반드시 node01~node08 표기(모니터링과 연결). 디자인은 §5 준수.
추가 아이디어가 있으면 이 두 페이지에 얹어도 좋아.
```

---

## 11. 최종 체크리스트

**개발 전**
- [ ] 이 문서를 새 세션에 첨부했다
- [ ] §3 파일·§4 DB·§6 API 경계를 셋이 함께 재확인했다
- [ ] 팀장이 공통 뼈대를 공유했다 (이후 병렬 시작)

**개발 중 (각자)**
- [ ] 내 소유 파일만 수정 (공통 파일 변경은 팀장 경유)
- [ ] 노드 표기 `node01`~`node08` 사용
- [ ] 내 API가 `/docs`에서 단독 응답

**통합·발표**
- [ ] 서버 하나로 5페이지 네비 이동 정상
- [ ] 채팅 위젯이 4개 페이지(index 제외)에 뜬다
- [ ] node_usage 등록 → 모니터링 카드 반영
- [ ] squeue/PBS에 없는 `mpirun` 직접 실행 작업도 node_usage 수동 등록으로 표시 가능
- [ ] 시연 시나리오(§9) 리허설 + 각자 자기 페이지 시연 분담

---

## 12. 라이브러리 / 의존성

### 백엔드 (`requirements.txt` — 팀장 소유)
```
fastapi              # 웹 프레임워크 + 자동 /docs (OpenAPI)
uvicorn[standard]    # ASGI 서버 (개발용 --reload)
```
- **사실상 이게 전부.** DB는 파이썬 표준 `sqlite3`(설치 불필요), 요청 본문 검증 `pydantic`은 fastapi가 자동 포함, 정적 서빙 `StaticFiles`는 fastapi/starlette 내장.
- **설치 안 해도 되는 것**(흔한 오해 방지): `python-multipart`(폼 업로드 안 씀 — JSON만), `jinja2`(서버 템플릿 안 씀 — 정적 HTML+fetch), `aiosqlite`/`sqlalchemy`(경량이라 raw `sqlite3`로 충분), `httpx`(서버 간 호출 안 함 — stats는 DB 직접 읽기).
- **재현성(채점 ② 재현·전파성 25점)**: 설치 후 버전을 **핀**해 두면 다른 PC에서 동일 재현. 예:
  ```bash
  pip install fastapi "uvicorn[standard]"
  pip freeze | grep -iE '^(fastapi|uvicorn|starlette|pydantic|anyio|click|h11)=' > requirements.txt
  # 새 PC: pip install -r requirements.txt
  ```
  (대략 `fastapi==0.11x`, `uvicorn==0.3x` 대 — 설치 시점 버전을 그대로 고정.)

### 프론트엔드 (설치 없음 — CDN/바닐라)
- **Chart.js 4.4.1** (CDN, 이미 `dev_part/monitoring.html`이 사용 중) — 모니터링 사용률 막대 + 통계 추이 차트.
  `https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js`
- **프레임워크 없음** — 순수 `fetch()` + `setInterval`(2~3초 폴링). React/Vue 불필요(셋업 과함).
- **오프라인 시연 대비**: CDN이 막히면 Chart.js 파일 1개만 `static/`에 내려받아 로컬 참조로 교체.

### 런타임
- **Python 3.9+** 권장. 표준 `sqlite3`/`datetime`/`json`만 사용해 추가 런타임 의존성 없음.

---

## 13. 유용한 스킬·기법 (가산점 ①과 직결)

> 해커톤은 **서브에이전트·도구연동·재사용 산출물**에 가산점(활용 점수 ①). 아래는 이 프로젝트 단계별로 바로 쓸 수 있는 것 — 슬래시 명령으로 호출.

### 개발 가속
- **`/run`** — uvicorn 앱을 띄워 변경이 실제로 도는지 즉시 확인.
- **서브에이전트 역할분담 (가점 a)** — 팀장 본인 작업도 병렬화 가능: 예) "모니터링 라우터 구현" + "squeue/sinfo 파서" 동시 진행. §10 킥오프 프롬프트가 곧 팀원별 에이전트 프롬프트(= 재사용 자산).

### 디버깅·검증
- **`/investigate`** — API가 빈 응답/500일 때 근본 원인 추적.
- **`/verify`** — "node_usage 등록 → 모니터링 카드 반영"이 실제 동작하는지 앱을 돌려 관찰 검증.
- **`/browse` · `/qa`** — 헤드리스 브라우저로 5페이지 자동 점검·버그 수정(채팅 폴링·네비 이동·차트 렌더). **데모 직전 필수.**

### 품질·일관성
- **`/design-review`** — 5페이지의 간격·위계·색상 토큰(§5) 불일치, AI 슬롭 패턴을 잡아 통일감 확보.
- **`/code-review`** — 통합 직전 라우터 5개 diff의 정확성·중복 점검.

### 발표·문서 (결과 30점 + 전파성)
- **`/diagram`** — §7 통합 접점·§9 데이터 흐름을 발표용 다이어그램 한 장으로.
- **`/make-pdf`** — 이 DEV_BLUEPRINT를 발표 배포본 PDF로.
- **`/document-generate`** — 빠진 README·사용설명 자동 생성.

### 세션 연속성 (1.5일)
- **`/context-save` · `/context-restore`** — 점심·저녁으로 세션이 끊겨도 작업 맥락 복구.
- **재사용 산출물 (가점 c)** — 이 `DEV_BLUEPRINT.md`, §10 킥오프 프롬프트, 프로젝트 `CLAUDE.md` 자체가 제출 자산. `submit/assets/`에 모아 점수화.

---

### 부록: 빠른 실행
```bash
pip install fastapi uvicorn
uvicorn main:app --reload --port 8000
# http://localhost:8000  ·  API 문서 /docs
```

---

## 14. 엔지니어링 검토 반영 (잠금 결정)

`/plan-eng-review`(2026-06-30)에서 6건을 잠갔다. **상세·구현 지침은 `SPEC.md` §13**을 단일 기준으로 따른다. 요약:

- **1A** `db.py` 동시성 표준(요청별 연결 + `check_same_thread=False` + WAL + `busy_timeout`) — 데모 중 `database is locked` 차단.
- **2A** 멱등 초기화(`CREATE TABLE IF NOT EXISTS` + 비었을 때만 시드) — `--reload` 재부팅 안전.
- **3A** `node_usage`는 노드별 최신 1건만 카드 표시(§7-1 반영).
- **4A** `_nav.html` JS 인클루드 자가주입 + `pathname` `.active`(§3 `static` 반영).
- **5A** 파서 입력 가드(헤더/빈줄/`int` 예외) — 부팅 무중단.
- **6A** pytest 최소 세트(파서·멱등시드·node키정합·TestClient 200).

> 5건이 팀장 공통 뼈대에 모인다. §8-1 공통 뼈대 공유 **전에** 1A·2A·4A·5A를 박아 둘 것.
