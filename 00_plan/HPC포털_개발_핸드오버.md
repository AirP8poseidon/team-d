# 사내 HPC 포털 — 개발 핸드오버 문서

> **이 문서의 용도**: 경연장에서 **새 세션을 열어 처음부터 시작**할 때, 이 문서 하나만 있으면 팀 전체가 바로 개발에 착수할 수 있도록 정리한 핸드오버입니다. 새 세션의 AI에게 이 문서를 첨부/붙여넣기 하면 맥락이 그대로 이어집니다.

---

## 0. 한 줄 요약

SLURM/PBS가 안 주는 **"사람의 맥락(누가·왜)"과 "실시간 소통"** 을 얹은 사내 HPC 통합 포털을, **FastAPI + SQLite 경량 풀스택**으로, **3명이 기능 1개씩 독립 개발 후 통합**한다. 데이터는 **SLURM 샘플 출력 목업**으로 시작한다.

---

## 1. 프로젝트 개요

### 무엇을 만드나
사내 HPC 사용자를 위한 웹 포털. 페이지 3개로 구성:

| 페이지 | 내용 | 담당 |
|---|---|---|
| **모니터링** | 노드 상태 실시간 현황, job 큐, 자원(CPU/GPU/메모리) 사용률, **각 작업의 사용자·목적 표시** | 팀장 |
| **정보공유(위키)** | 서버별 환경 구성·사용법 안내, 사용자 노하우 게시판(작성·검색) | 팀원1 |
| **실시간 채팅 + 사용현황** | 사용자 간 실시간 채팅, "지금 누가 어느 노드를 무슨 목적으로 쓰는 중" 보드 | 팀원2 |

### 왜 (발표 포지셔닝)
"SLURM 대시보드 재구현"이 아니라 **"SLURM이 못 채우는 협업·소통 레이어"** 다. 자원 숫자 위에 *사람의 맥락*과 *실시간 소통*을 얹어, 노드 충돌·중복 작업·문의 반복 같은 실제 불편을 줄인다. → 평가의 **업무 적용성 / 개선 효과 / 창의성** 항목을 정조준.

---

## 2. 확정된 기술 결정 (변경 금지 사항)

이 결정들은 경연 전 합의 완료. 새 세션에서 흔들지 말 것.

- **아키텍처**: 경량 풀스택. **Python FastAPI + SQLite** 단일 백엔드, 프론트는 정적 HTML/JS.
- **데이터 소스**: 실서버 연동 안 함. **`squeue`/`sinfo` 샘플 출력(텍스트 파일)을 파싱**해서 시작. (시간 남으면 실연동은 옵션)
- **실시간**: WebSocket 안 씀. **2~3초 폴링(polling)** 으로 채팅·현황 갱신. (1.5일 내 안정성 우선)
- **레포 구조**: 단일 레포, 단일 FastAPI 앱. 기능별로 **파일을 분리**해 충돌 방지.
- **언어/디자인**: 한국어. 공통 색상·폰트·상단 네비게이션은 아래 계약(§4)을 따른다.

---

## 3. 전체 아키텍처

```
[브라우저]
   │  (HTML 페이지 3개 + 공통 헤더)
   ▼
[FastAPI 앱]  ── 정적 페이지 서빙 + REST API
   │
   ├── /api/monitoring/*   (팀장)
   ├── /api/wiki/*         (팀원1)
   └── /api/chat/*         (팀원2)
   │
   ▼
[SQLite DB]   ── 기능별 테이블 분리
   ▲
   │ (시작 시 1회 적재)
[data/sample_squeue.txt, sample_sinfo.txt]  ← SLURM 목업
```

**핵심 원리**: 세 사람이 같은 파일을 동시에 만지지 않는다. 각자 **자기 라우터 파일 + 자기 페이지 + 자기 DB 테이블**만 건드린다. 충돌(merge conflict) 원천 차단.

---

## 4. 인터페이스 계약 (★ 가장 중요 — 병렬 개발의 핵심)

세 명이 서로 안 기다리고 독립적으로 일하려면 "경계"를 미리 못 박아야 한다. 아래는 **건드리면 안 되는 공통 약속**.

### 4-1. 폴더/파일 구조

```
hpc-portal/
├── main.py                 # FastAPI 앱 진입점, 라우터 등록, 정적 서빙   [팀장]
├── db.py                   # SQLite 연결 + 테이블 초기화                  [팀장]
├── requirements.txt        # fastapi, uvicorn                            [팀장]
├── data/
│   ├── sample_squeue.txt   # job 목업                                     [팀장]
│   └── sample_sinfo.txt    # 노드 목업                                    [팀장]
├── routers/
│   ├── monitoring.py       # /api/monitoring/*                           [팀장]
│   ├── wiki.py             # /api/wiki/*                                  [팀원1]
│   └── chat.py             # /api/chat/*                                  [팀원2]
└── static/
    ├── common.css          # 공통 테마 + 네비게이션 스타일               [팀장]
    ├── _nav.html           # 공통 상단 메뉴 스니펫(복붙용)               [팀장]
    ├── index.html          # 랜딩                                        [팀장]
    ├── monitoring.html     # 모니터링 화면                               [팀장]
    ├── wiki.html           # 위키 화면                                   [팀원1]
    └── chat.html           # 채팅+현황 화면                              [팀원2]
```

> 각자 자기 이름이 붙은 파일만 수정. `main.py`·`db.py`·`common.css`·`_nav.html` 같은 공통 파일은 **팀장만** 수정.

### 4-2. 공통 규칙 (디자인 토큰)

- `<html lang="ko">`, 폰트 `"Malgun Gothic","Apple SD Gothic Neo",Arial,sans-serif`
- 색상 변수: `--bg:#f4f6fb; --paper:#fff; --ink:#172033; --muted:#64748b; --line:#d8dee9; --blue:#1d4ed8; --navy:#0f172a; --green:#047857; --orange:#b45309; --red:#b91c1c`
- 상단 네비: 네이비 배경, 좌측 "사내 HPC 포털", 우측 링크 `홈 / 모니터링 / 정보공유 / 실시간 채팅` → `index.html / monitoring.html / wiki.html / chat.html`. 현재 페이지 강조.
- **노드 명명 규칙(통합용 필수)**: `node01` ~ `node08`. 세 기능 모두 이 표기를 사용해야 모니터링 ↔ 채팅 현황이 연결됨.
- 시간 표기: 화면용은 `"HH:MM"`, 저장은 ISO 문자열.

### 4-3. DB 테이블 (소유자별, 서로 안 겹침)

```
-- [팀장] 모니터링
nodes(node TEXT PK, status TEXT, cpu INT, gpu INT, mem INT, gpu_model TEXT)
jobs(job_id TEXT PK, user TEXT, node TEXT, purpose TEXT, status TEXT, elapsed TEXT)

-- [팀원1] 위키
servers(id INTEGER PK, name TEXT, os TEXT, spec TEXT, modules TEXT, ssh TEXT)
posts(id INTEGER PK, title TEXT, author TEXT, body TEXT, created_at TEXT)

-- [팀원2] 채팅 + 현황
messages(id INTEGER PK, sender TEXT, body TEXT, created_at TEXT)
node_usage(id INTEGER PK, node TEXT, user TEXT, purpose TEXT, eta TEXT, created_at TEXT)
```

### 4-4. API 엔드포인트 (소유자별)

```
[팀장]   GET  /api/monitoring/nodes      → 노드 목록(상태·자원)
         GET  /api/monitoring/jobs       → job 큐(사용자·목적 포함)

[팀원1]  GET  /api/wiki/servers          → 서버 환경 목록
         GET  /api/wiki/posts?q=검색어   → 게시글 목록(검색)
         POST /api/wiki/posts            → 게시글 작성 {title, author, body}

[팀원2]  GET  /api/chat/messages?after=id → 신규 메시지(폴링)
         POST /api/chat/messages         → 메시지 전송 {sender, body}
         GET  /api/chat/usage            → 현재 사용현황 목록
         POST /api/chat/usage            → 사용현황 등록 {node, user, purpose, eta}
```

### 4-5. 통합 접점 (단 하나, 막판에 팀장이 연결)

채팅의 `node_usage`(누가 어느 노드를 무슨 목적으로) ↔ 모니터링 화면의 노드 카드/잡 표.
→ **노드 명명(`node01`…`node08`)만 일치시키면**, 팀장이 모니터링 화면에서 `/api/chat/usage`를 같이 호출해 "현재 작업 목적"을 노드에 매칭 표시. 이게 "세 페이지가 한 흐름으로 이어지는" 데모의 하이라이트.

---

## 5. 개발 프로세스 & 타임라인 (Day 1 / Day 2)

> 보고서 일정(Day1 11:00 시작)에 맞춰 매핑. 시간은 가이드.

### Day 1 — 집중 개발
| 시간 | 단계 | 내용 |
|---|---|---|
| 11:00–11:30 | 행사 안내 | 착석, 운영 안내 |
| 11:30–12:00 | **0단계: 스펙·계약 확정** | 이 문서 §1·§4를 팀이 함께 재확인. 노드 명명·DB·API 경계 합의 못 박기 |
| 12:00–13:00 | 점심 | 아이디어 자유 논의 |
| 13:00–13:40 | **1단계: 공통 뼈대(팀장)** | 팀장이 `main.py`·`db.py`·`common.css`·`_nav.html` + 빈 페이지 3개 생성 후 **즉시 공유**. 이게 출발 신호 |
| 13:40–18:00 | **2단계: 병렬 개발** | 셋이 각자 자기 라우터+페이지+테이블 독립 개발 |
| 18:00–19:00 | 저녁 + 1차 통합 | 진행 공유, 각 API가 도는지 첫 합치기 시도 |
| 19:00–21:30 | **3단계: 통합·보완·발표 준비** | 팀장이 통합 접점(현황↔모니터링) 연결, 버그 보완, 시연 리허설 |
| 21:30–22:00 | 마무리 | 코드 저장, 발표자료 제출 |

### Day 2 — 평가
발표·시연(팀별), 각자 자기가 만든 페이지를 직접 시연 → 질의응답 → 평가/시상.

**철칙**: 1단계(공통 뼈대 공유) 전에는 아무도 본문 개발을 시작하지 않는다. 뼈대가 나오면 그때 셋이 흩어진다. 단, 뼈대는 "완성"이 아니라 헤더+빈 틀 수준이면 충분(40분 내).

---

## 6. 인원별 개발 방향

### 👑 팀장 (나) — 통합 책임 + 모니터링
가장 어렵고(데이터 파싱) 공통 부분을 쥐는 역할. **남보다 먼저, 남보다 늦게** 끝난다(뼈대 먼저 → 통합 마지막).

- **소유 파일**: `main.py`, `db.py`, `common.css`, `_nav.html`, `index.html`, `routers/monitoring.py`, `static/monitoring.html`, `data/*.txt`
- **할 일 순서**
  1. FastAPI 뼈대(`main.py`) + SQLite 초기화(`db.py`) + 공통 헤더/CSS + 빈 페이지 3개 → **13:40까지 공유**
  2. `sample_squeue.txt`/`sample_sinfo.txt` 목업 작성 → 파서 → `nodes`/`jobs` 테이블 적재
  3. `GET /api/monitoring/nodes`, `/jobs` 구현
  4. `monitoring.html`: KPI 카드 + 노드 그리드(CPU/GPU/메모리 막대) + job 큐 표(사용자·목적). *(이전 프로토타입 `monitoring.html` 재사용 가능)*
  5. **막판 통합**: 4페이지 한 폴더로 + 채팅 `node_usage`를 모니터링 노드에 매칭 표시 + 메뉴 링크 점검
- **완료 기준**: 모니터링 화면이 API에서 데이터를 받아 렌더되고, 노드에 "현재 작업 목적"이 뜬다.

### 🧑‍💻 팀원1 — 정보공유(위키)
표준 CRUD라 가장 안정적으로 완성 가능. *"빈 화면에서 내가 통째로 만든다"* 경험에 적합.

- **소유 파일**: `routers/wiki.py`, `static/wiki.html`
- **건드리지 않을 것**: 공통 파일(`main.py` 등)은 팀장에게 요청. 자기 라우터는 `main.py`에 한 줄 등록만 팀장이 해줌.
- **할 일 순서**
  1. `servers` 테이블에 서버 3대(gpu-cluster/cpu-cluster/fat-node) 환경정보 시드
  2. `GET /api/wiki/servers` → 화면에 서버 환경 카드 렌더
  3. `posts` 테이블 + `GET /api/wiki/posts?q=` (검색) + `POST /api/wiki/posts` (작성)
  4. `wiki.html`: 서버 환경 카드 + 사용법 가이드(ssh→module/conda→sbatch) + 노하우 게시판(검색창·글쓰기 폼). *(이전 프로토타입 `wiki.html` 재사용 가능)*
- **완료 기준**: 글 작성 → DB 저장 → 목록·검색에 반영. 서버 환경정보가 화면에 표시.

### 🧑‍💻 팀원2 — 실시간 채팅 + 사용현황 보드
폴링이라 비교적 단순하지만 "실시간 느낌"으로 데모 임팩트가 큼.

- **소유 파일**: `routers/chat.py`, `static/chat.html`
- **통합 주의**: `node_usage`의 `node` 값은 반드시 `node01`~`node08` 표기 사용(팀장 모니터링과 연결됨).
- **할 일 순서**
  1. `messages` 테이블 + `POST /api/chat/messages` (전송) + `GET /api/chat/messages?after=id` (폴링)
  2. `chat.html` 채팅창: 2~3초마다 `after` 폴링으로 신규 메시지 표시, 내 메시지 우측 말풍선
  3. `node_usage` 테이블 + `GET/POST /api/chat/usage`
  4. "지금 누가 뭐 쓰는 중" 보드 + 등록 폼(노드·사용자·목적·예상시간). *(이전 프로토타입 `chat.html` 재사용 가능)*
- **완료 기준**: 메시지 전송 → 저장 → 폴링으로 상대 화면에 표시. 사용현황 등록 → 보드 반영(+모니터링과 연결될 준비 완료).

---

## 7. 통합 절차 (Day1 저녁, 팀장 주도)

1. 세 사람의 `routers/*.py`를 한 레포 `routers/`에 모으고, `main.py`에 3개 라우터 등록(이미 자리 잡혀 있음).
2. `static/`에 4개 HTML + `common.css` + `_nav.html` 모으기.
3. 서버 1개(`uvicorn main:app`) 띄워서 메뉴 4칸 이동 확인.
4. **통합 접점 연결**: `monitoring.html`이 `/api/chat/usage`도 호출 → 노드별 "현재 작업 목적" 표시.
5. 스모크 테스트: 채팅에 현황 등록 → 모니터링에서 보이나? 위키 글 작성 → 저장되나?

> 파일이 처음부터 분리돼 있어 "합치기"는 사실상 **파일을 한 폴더에 모으는 것 + 접점 1개 연결**이 전부.

---

## 8. 시연 시나리오 (발표용 — 한 흐름으로)

1. **채팅**: 사용자가 "node04 딥러닝 학습 시작합니다, ~18시" 입력 + 현황 보드에 등록
2. **모니터링**: node04 카드에 사용자·작업목적이 즉시 표시, job 큐·GPU 사용률 확인
3. **위키**: 그 서버(gpu-cluster) 환경·sbatch 사용법을 위키에서 확인
4. 메시지: "SLURM은 자원을, 우리 포털은 **사람의 맥락과 소통**을 더한다"

→ 세 페이지(=세 사람 작업)가 끊김 없이 이어지는 걸 보여주면 통합·완성도·창의성 점수가 함께 올라간다. 발표 시 **각자 자기 페이지를 직접 시연**(기여도 가시화).

---

## 9. 새 세션 부트스트랩용 킥오프 프롬프트

경연장에서 **새 세션을 열고, 이 문서를 첨부/붙여넣은 뒤**, 각자 아래를 복사해 시작하면 된다.

### (A) 팀장 — 공통 뼈대부터
```
나는 HPC 포털 프로젝트 팀장이야. 첨부한 핸드오버 문서(§4 인터페이스 계약)를 그대로 따른다.
먼저 공통 뼈대만 만들어줘:
- FastAPI 앱(main.py), SQLite 초기화(db.py), requirements.txt
- 공통 헤더 스니펫(_nav.html)과 common.css (문서 §4-2 디자인 토큰 준수)
- 빈 페이지 4개(index/monitoring/wiki/chat) — 헤더만 들어간 상태
- routers/ 에 monitoring.py, wiki.py, chat.py 빈 라우터 + main.py에 등록
이게 끝나면 모니터링 기능(routers/monitoring.py + monitoring.html)을 §6 팀장 항목대로 이어서 개발해줘. 데이터는 §4-3 스키마, 목업 squeue/sinfo 파싱.
```

### (B) 팀원1 — 위키
```
나는 HPC 포털 팀의 팀원1, 정보공유(위키) 페이지 담당이야. 첨부 핸드오버 문서를 따른다.
내 소유 파일은 routers/wiki.py 와 static/wiki.html 뿐이야(공통 파일은 건드리지 않음).
§4-3의 servers/posts 테이블, §4-4의 /api/wiki/* 엔드포인트, §6 팀원1 단계대로
서버 환경 카드 + 사용법 가이드 + 검색되는 노하우 게시판을 만들어줘. 디자인은 §4-2 준수.
```

### (C) 팀원2 — 채팅 + 현황
```
나는 HPC 포털 팀의 팀원2, 실시간 채팅 + 사용현황 보드 담당이야. 첨부 핸드오버 문서를 따른다.
내 소유 파일은 routers/chat.py 와 static/chat.html 뿐이야(공통 파일은 건드리지 않음).
§4-3의 messages/node_usage 테이블, §4-4의 /api/chat/* 엔드포인트, §6 팀원2 단계대로
2~3초 폴링 채팅 + "지금 누가 뭐 쓰는 중" 보드(등록 폼)를 만들어줘.
node 값은 반드시 node01~node08 표기 사용(모니터링과 연결됨). 디자인은 §4-2 준수.
```

> **팁**: 같은 팀이 한 세션을 공유하지 않는다면, 각자 자기 세션에서 위 프롬프트 + 이 문서로 자기 파일만 만든 뒤, 팀장이 파일을 모아 통합한다.

---

## 10. 최종 체크리스트

**개발 전**
- [ ] 이 문서를 새 세션에 첨부했다
- [ ] §4 계약(파일/DB/API/노드 명명)을 셋이 함께 재확인했다
- [ ] 팀장이 공통 뼈대를 공유했다 (이후 병렬 시작)

**개발 중 (각자)**
- [ ] 내 소유 파일만 수정하고 있다 (공통 파일 변경은 팀장 경유)
- [ ] 노드 표기 `node01`~`node08` 사용
- [ ] 내 API가 단독으로 응답한다 (`/docs`에서 확인)

**통합·발표**
- [ ] 서버 하나로 4페이지 이동 정상
- [ ] 채팅 현황 → 모니터링에 표시되는 접점 연결됨
- [ ] 시연 시나리오(§8) 리허설 완료
- [ ] 각자 자기 페이지 시연 분담 정함

---

### 부록: 빠른 실행
```bash
pip install fastapi uvicorn
uvicorn main:app --reload --port 8000
# 브라우저: http://localhost:8000
```

