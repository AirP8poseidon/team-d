# PROCESS_LOG — 작업 기록 (과정 70점의 핵심 근거)

> 원칙: **실제로 시킨 프롬프트를 그대로 인용**. 의미 있는 단계마다 1개씩 누적.

## 작성자 정보 (개인별 로그 — 본인 것만)
- 팀명: team-d (한글 팀명: 미정 — 작업 중 확정)
- 본인 이름(작성자): 김민주 (kimminju)
- 공통과제(우리 팀이 자동화한 반복 수작업): 사내 HPC 통합 포털 — SLURM이 안 주는 "누가·왜 쓰는지(사람 맥락) + 실시간 소통 + 운영 가시성"을 얹어, 노드 사용 정보·노하우를 매번 구두/메신저로 묻고 흩어진 문서를 뒤지던 수작업을 웹으로 집약.
- 내가 맡은 부분: **정보공유(위키) 페이지 + 자체주입 플로팅 실시간 채팅 위젯** (FastAPI 라우터 2개 + SQLite, 정적 HTML/JS)
- 자유과제(있으면): -

## 효과 측정 (Before → After)

| 지표(내 파트 기준) | Before(기존 수작업) | After(에이전트화) |
|------|------|------|
| 서버 환경·사용법 확인 | 매번 선임에게 구두 문의/흩어진 메모 검색 | 위키 1페이지에 서버 3대 환경+sbatch 가이드 집약, 즉시 열람 |
| 노하우 공유 | 메신저·개인 기록에 산재(검색 불가, 휘발) | 게시판에 누적 + 제목·본문 검색(`?q=`) |
| 노드 사용 소통 | "지금 node04 누가 써요?" 반복 문의 | 어느 페이지서든 플로팅 채팅으로 실시간 공유(2~3초 폴링) |
| 신규자 온보딩 | 환경/사용법을 일일이 물어봐야 함 | 위키 한 장으로 자가 학습 |
| 위젯 재사용성 | (없음) | `<script src="/static/chat-widget.js">` 한 줄로 4개 페이지에 동일 채팅 주입 |

## 사용 기법 (권장·가점)
- [x] (a) 서브에이전트 / 역할 분담 — 기능 확장 시 **채팅 담당 / 위키 담당 2개 서브에이전트에 파일 단위로 역할 분담**(소유 파일 분리로 충돌 없이 병렬 구현). (#6·#7)
- [x] (b) 외부 도구·데이터 연동 — FastAPI+SQLite 백엔드, 브라우저 프리뷰 MCP로 라이브 검증, fetch 폴링
- [x] (c) 재사용 산출물 — 자체주입 `chat-widget.js`(한 줄 로드), `dev_run.py` 단독 실행 하네스, 킥오프 프롬프트셋

---

## 작업 로그 (단계마다 1개씩 누적 / 시간순)

### [#1] 깃헙 연결 + 개인 브랜치 셋업
- 작성자(팀원): 김민주(kimminju)
- 목표: 팀 저장소(team-d)에 연결하고, main을 안 건드리는 개인 브랜치 작업 흐름 구성
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "로컬에서 작업하고 내가 push하면 브런치에 업데이트하는 로직으로 해야해"
- 사용한 기법(있으면): (b 도구연동 — gh CLI, git)
- 결과: gh device-flow 로그인(kimminju000825-cpu) → `~/.config` 권한 복구 → `AirP8poseidon/team-d` clone → 개인 브랜치 `kimminju` 생성·push, upstream 추적 설정. push 권한(push=true) 확인.
- 막힘 → 해결: gh가 `~/.config`(root 소유)에 설정 저장 실패 → `chown`으로 소유권 복구 후 재인증 성공.

### [#2] 팀 청사진 파악 + 내 역할·인터페이스 확정
- 작성자(팀원): 김민주(kimminju)
- 목표: 주장이 올린 최신 main을 받아 프로젝트 스펙과 내 소유 파일/DB/API 경계 확정
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "메인 브런치 업데이트 됐을거야 긁어와서 읽어"
- 사용한 기법(있으면): (c 재사용 산출물 — DEV_BLUEPRINT/핸드오버 문서를 단일 진실 공급원으로 사용)
- 결과: `git fetch` 후 `DEV_BLUEPRINT.md`·`member1_wiki_chat.md` 정독. 팀원1 소유 = `routers/wiki.py`,`routers/chat.py`,`static/wiki.html`,`static/chat-widget.js`. DB(servers/posts/messages), API 경계, 디자인 토큰(§5), 노드 명명 규칙 확인. 공통 파일(main.py/db.py)은 팀장 소유라 안 건드리기로.

### [#3] 위키·채팅 백엔드 구현 (FastAPI 라우터 + SQLite)
- 작성자(팀원): 김민주(kimminju)
- 목표: `/api/wiki/*`, `/api/chat/*`가 팀장 코드 없이 `/docs`에서 단독 응답하도록(통합 전제)
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "팀원1 — 위키 + 채팅위젯" (역할 확정) → DEV_BLUEPRINT §4 DB·§6 API대로 구현
- 사용한 기법(있으면): (b 도구연동)
- 결과: `routers/wiki.py`(servers 시드 3대, posts 시드 8건, GET servers/posts·q검색·POST), `routers/chat.py`(messages GET after폴링·POST). **통합 안전 설계**: 각 라우터가 `CREATE TABLE IF NOT EXISTS`+빈 경우만 시드 → 팀장 db.py 유무와 무관하게 단독 동작. DB는 `HPC_DB` 환경변수로 공유.
- 막힘 → 해결: db.py가 팀장 소유라 의존 불가 → 라우터가 자기 테이블을 멱등 보장하는 방식으로 디커플링.

### [#4] 위키 화면 API 연동 + 자체주입 채팅 위젯
- 작성자(팀원): 김민주(kimminju)
- 목표: 디자인 완성된 프로토타입(가짜 JS 배열)을 진짜 API에 배선 + 한 줄로 뜨는 채팅 위젯
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "userA_part/wiki.html 재사용" + "다른 페이지가 `<script src="/static/chat-widget.js">` 한 줄로 띄울 수 있게, CSS는 JS에서 `<style>` 주입하고 클래스는 cw- prefix"
- 사용한 기법(있으면): (c 재사용 산출물)
- 결과: `static/wiki.html` — 서버카드/게시판을 fetch로 동적 렌더, 검색 디바운스, 글쓰기 POST 즉시 반영, 네비 5링크로 갱신. `static/chat-widget.js` — IIFE 캡슐화, `<style>` 주입, 우하단 토글, 2.5초 폴링, 내 메시지 우측 말풍선, 이름 localStorage 보관, 안읽음 배지.

### [#5] 자동 검증 (API 8종 + 브라우저 위젯 왕복)
- 작성자(팀원): 김민주(kimminju)
- 목표: "글 작성→검색 반영", "메시지 전송→폴링 수신" 등 완료 기준을 실제로 돌려 검증
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "AI가 높은 점수를 주는 방향으로 기록물 저장해" + 동작 검증
- 사용한 기법(있으면): (b 도구연동 — FastAPI TestClient, 브라우저 프리뷰 MCP)
- 결과: TestClient로 8개 엔드포인트 ALL PASS(서버3·게시글8·검색·작성·채팅시드·전송·after폴링). 브라우저 프리뷰로 위키 렌더 확인, 채팅 위젯에서 "node04 딥러닝 시작합니다 ~18시" 전송 → 폴링 반영 → 우측 말풍선(14:08), 메시지 3개 확인.

### [#6] 채팅 차별화 — 노드 점유 "선언" 보드 + 메시지 검색
- 작성자(팀원): 김민주(kimminju)
- 목표: SLURM 실측이 안 주는 "사람 맥락(누가·왜·언제까지 노드를 쓸 계획인지)"을 선언 보드로 + 채팅 기록 검색
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "우리 차별점은 SLURM이 안 주는 사람 맥락 — 누가·왜·언제까지 노드를 쓸 계획인지다. 그 계획/의도 선언을 담는다(실측 아님)." / "GET /api/chat/messages 에 q 파라미터 추가… q가 없으면 기존 after 동작을 그대로 유지(폴링 호환 필수)"
- 사용한 기법(있으면): (b 도구연동 — FastAPI TestClient 검증, 멱등 init_db 시드)
- 결과: `routers/chat.py`에 `reservations` 테이블(멱등 생성+시드2건) 및 3개 엔드포인트(GET/POST/`{rid}/release`) 추가, `/messages`에 `q` LIKE 검색(body·sender) 추가하며 after 폴링 호환 유지. `chat-widget.js`에 헤더 아래 "📌 지금 점유 중" 핀 섹션(5초 폴링, 본인 who면 해제 버튼), ＋점유선언 미니폼, 🔍 검색 토글(200ms 디바운스, searchMode 플래그로 폴링이 검색결과를 덮어쓰지 않게 보호) 추가. 모두 `cw-` prefix·기존 색감 유지.
- 검증: 임시 DB로 TestClient 실행 — 시드2건 로드, POST 생성, 빈 node/who 거절, release 후 활성 3→2, `q=점검` LIKE 매칭, 빈 q == after=0 동일 길이 ALL PASS.

### [#7] 위키 기능 확장 — 태그+도움됐어요 / 상세+댓글
- 작성자(팀원): 김민주(kimminju)
- 목표: 노하우 게시판을 분류·평가·토론 가능한 진짜 위키로 격상(태그 필터·인기순·👍·상세 아코디언·댓글)
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "posts 테이블에 컬럼 추가: tags TEXT DEFAULT '', helpful INTEGER DEFAULT 0. 기존 DB 호환 위해 마이그레이션 안전하게: PRAGMA table_info(posts)로 컬럼 존재 확인 후 없으면 ALTER TABLE … (SQLite는 ADD COLUMN IF NOT EXISTS 미지원이니 직접 체크)" / "게시글 제목 클릭 시 상세 펼침(아코디언… 새 페이지 만들지 마라). 상세에 본문 전체 + 댓글 목록 + 댓글 작성 폼"
- 사용한 기법(있으면): (b 도구연동 — PRAGMA 기반 무손실 마이그레이션, FastAPI TestClient 검증)
- 결과: `routers/wiki.py` — posts에 `tags`/`helpful` 컬럼 멱등 마이그레이션(PRAGMA 체크 후 ALTER), 시드8건 태그 부여, `comments` 테이블(시드3건, post 1·3에 부착). 신규 엔드포인트 5종: `GET /posts/{pid}`, `POST /posts/{pid}/helpful`, `GET·POST /posts/{pid}/comments`, 그리고 `/posts`에 `tag`·`sort=helpful` 파라미터(q와 AND). `static/wiki.html` — 태그 칩 필터줄, 인기순/최신순 토글, 카드별 👍버튼(숫자만 갱신)·태그 칩, 제목클릭 상세 아코디언(본문+댓글+작성폼), 글쓰기 폼 태그 입력칸. 기존 q검색·디바운스·채팅위젯 한 줄 유지.
- 검증: 신규 DB로 지정 검증 스크립트 ALL OK(tags 배열·helpful·tag필터2건·helpful+1·상세·댓글시드·추가). 추가로 **실제 hpc.db 복제본**에 대해 9건 무손실 마이그레이션(tags 빈배열·helpful 키 생성)·sort=helpful 정렬·배열형 tags 입력·빈 댓글 거절·없는 글 not found 모두 PASS. 원본 hpc.db·임시 DB 미오염 확인.

### [#8] 서브에이전트 역할 분담(병렬) + 통합 검증
- 작성자(팀원): 김민주(kimminju)
- 목표: 추가 기능 4종을 충돌 없이 빠르게 — 파일 소유가 겹치지 않게 2개 서브에이전트에 분담해 **병렬** 구현하고, 내가 직접 통합 검증
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "서브 에이전트 쓰고 싶어" → (오케스트레이션) "에이전트 A(채팅)=routers/chat.py+chat-widget.js / 에이전트 B(위키)=routers/wiki.py+wiki.html. **너의 소유 파일은 딱 둘… 다른 파일은 절대 건드리지 마라**(다른 에이전트가 동시에 수정 중)"
- 사용한 기법(있으면): **(a 서브에이전트/역할분담)** + (b 도구연동 — 통합 TestClient 17종, 프리뷰 MCP)
- 결과: 두 서브에이전트를 **단일 메시지로 병렬 실행**(파일 소유 분리 → 머지 충돌 0). 산출: 채팅=노드 점유 선언 보드(reservations 테이블+3엔드포인트)·메시지 q검색 / 위키=태그+👍(무손실 컬럼 마이그레이션)·상세+댓글(comments 테이블+5엔드포인트). 보고만 믿지 않고 **내가 직접 통합 검증**: 깨끗한 임시 DB로 기존+신규 17개 엔드포인트 TestClient ALL PASS(회귀 0), 프리뷰 MCP로 태그 칩/👍/인기순/상세 아코디언+댓글·채팅 점유 보드/검색 라이브 확인.
- 막힘 → 해결: 루트 `hpc.db`가 구 스키마(5컬럼)라 ALTER만으론 기존 글에 시드 태그 미부여 → dev DB 재시드로 데모 일관성 확보(운영 통합 시엔 멱등 마이그레이션이 자동 적용).

---
### [#9] 위키 화면 리디자인 + 통합 락(T7) 선반영 + 최소 pytest
- 작성자(팀원): 김민주(kimminju)
- 목표: 기능은 됐으나 "안 예쁜" 위키 레이아웃을 다듬고, main 업데이트의 엔지니어링 락 중 내 파트 해당분(T7 채팅 초기 로드 50개 제한)을 미리 반영 + 재현성(채점 동점 1순위)을 위해 라우터 최소 자동 테스트 추가.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "지금 페이지 구성이 별로야. 기능은 좋은데 클러스터 사용 방법, 게시판 등 페이지 구성이 안예뻐" / "업데이트된거 보고 내가 수행해야할 내용 없어? API 연동 방식이라던가" / "일단 반영하고 결과물 보여줘 지금까지 된거 눈으로 확인하게"
- 사용한 기법(있으면): (b 도구연동 — pytest+TestClient 자동 검증, 프리뷰 MCP 라이브 확인) · (c 재사용산출물 — tests/ 디렉터리)
- 결과: ①위키 리디자인 — 히어로 헤더(네이비→블루 그라데이션+요약 pill), 섹션 아이콘 배지(🖥️📘💡), 서버 카드 상단 컬러 액센트(GPU 녹/CPU 청/대용량 주황)+호버 리프트, 그라데이션 스텝 원, 글 카드 호버. **JS 바인딩 클래스·ID·디자인 토큰은 그대로 보존**(회귀 0, 콘솔 오류 0). ②T7 반영 — `GET /api/chat/messages` 초기 로드(after 없음)는 `ORDER BY id DESC LIMIT 50` 후 시간순 복원, 폴링(after>0)은 증분 그대로. ③최소 테스트 — `tests/`에 위키·채팅 스모크+게시글/검색+점유보드+**T7 50개 제한**+**멱등 시드** 10케이스, 임시 DB로 실행 **10 passed**(실 hpc.db 미접촉).
- 막힘 → 해결: 라우터가 import 시점에 `HPC_DB`로 경로를 고정 → `conftest.py`에서 import "이전"에 `tempfile` 임시 DB를 지정해 실제 데이터 보호. 1A(get_db 일원화)·2A(중앙 init)는 팀장 `db.py` 공개 전까지 보류(현재 자체 `_conn()`+멱등 시드로 /docs 단독 응답 유지).

---
### [#10] SPEC 규격 대조 — 내 파트 인수조건(§7/§8/§13) 점검·보정
- 작성자(팀원): 김민주(kimminju)
- 목표: "통합 호환 규격(SPEC)에 내 코드가 실제로 맞는지"를 말이 아니라 코드로 1:1 대조하고, 어긋난 곳을 즉시 보정.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "통합했을 때 호환되게 맞추는 규격서 그럼 이거 맞췄어??"
- 사용한 기법(있으면): (b 도구연동 — 라이브 API 필드 덤프 + grep 토큰 대조)
- 결과: **합격** — §7.2 servers `{id,name,os,spec,modules,ssh}` 정확 일치 / posts 필수 5필드 충족(+tags·helpful 상위호환) / §7.3 messages `{id,sender,body,created_at}` 정확 일치 / 노드 키 `node01~08`(reservations 시드 node04·node07, T8 정합) / 2A 멱등·6A pytest·T7 반영 확인. **보정 1건** — §8 디자인 토큰 3개가 리디자인 중 드리프트(`--bg #eef1f8→#f4f6fb`, `--line #e2e8f0→#d8dee9`, `--red` 누락→`#b91c1c` 추가)해서 SPEC 값으로 되돌림(추가 토큰 --radius/--shadow는 비충돌이라 유지). 회귀 0.
- 막힘 → 해결: 1A(`get_db()` 일원화)·4A(`_nav.html` JS 인클루드)는 팀장 공통 뼈대(`db.py`/`_nav.html`)가 아직 repo에 없어 지금은 물리적으로 불가 → 통합 시점에 `_conn()`→`get_db()` 한 줄, 하드코딩 nav→스니펫 한 줄로 교체 예정(누락 아닌 보류).

---
### [#11] 팀장 통합 스캐폴딩(hpc-portal) 수용 + 내 4파일 포팅 + 전체 앱 실행 검증
- 작성자(팀원): 김민주(kimminju)
- 목표: 팀장이 main에 올린 공통 뼈대(`hpc-portal/`: 중앙 `db.py`+`main.py`+5라우터+공통 nav/CSS)를 머지해 숙지하고, 내 차별화 기능(태그·👍·댓글 / 점유 보드·검색)을 **플레이스홀더 위에 포팅**해 단일 앱으로 실제 구동·검증.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "일단 메인 브랜치에 뼈대 업데이트 됐거든? 업데이트된 메인 다시 긁어와서 숙지하고 다음 계획 말해줘. 아마 이제 직접 런하는 그런거 같아" → "진행해줘"
- 사용한 기법(있으면): (b 도구연동 — 통합 TestClient 11종, 프리뷰 MCP 라이브 확인) · (c 재사용산출물 — hpc-portal/tests에 차별화 기능 테스트 6종 추가)
- 결과: ①머지 — `git merge origin/main`로 hpc-portal 스캐폴딩 33파일 수용, 개인 로그 충돌(submit/*.md)은 규칙대로 내 버전 유지. ②포팅 — 자체 `_conn()`/`init_db()` 방식을 **중앙 `db_dep` 의존성**으로 전환(결정 1A 준수), 중앙 스키마(posts 5컬럼·comments/reservations 없음)를 건드리지 않고 **첫 요청 때 1회 멱등 가산**(posts.tags/helpful ALTER + comments/reservations CREATE IF NOT EXISTS)으로 차별화 기능 복원. 위키 화면은 하드코딩 nav·중복 토큰 제거 → `nav-placeholder`+`include.js`(4A)+`common.css`(§8) 사용. 채팅 위젯은 한 줄 로드 그대로. ③검증 — 깨끗한 임시 DB로 **TestClient 11 passed**(팀장 5 + 내 차별화 6), 실제 `uvicorn main:app`(8123) 구동 후 프리뷰 MCP로 라이브 확인: 5메뉴 nav 주입(정보공유 active)·서버 카드 3장·게시판(👍 버튼)·채팅 위젯 점유 보드(node04/node07)·검색까지 콘솔 오류 0.
- 막힘 → 해결: 중앙 `seed_if_empty()`가 messages는 의도적으로 시드 안 함(사용자 데이터 보존 정책) → 채팅 초기 0건이 정상임을 확인하고 위젯 빈 상태 처리 유지. 태그 칩은 중앙 시드 글에 태그가 없어 숨김(태그 글 생성 시 자동 노출) — 회귀 아님.

---
### [#12] 통합본 데모 데이터 보강 — 빈 화면 → 차별화 기능이 한눈에
- 작성자(팀원): 김민주(kimminju)
- 목표: 통합본이 중앙 `seed_if_empty()`의 최소 글 3건(태그 없음)만 보여 "내 페이지가 비어 보인다"는 문제를, 팀장 소유 `db.py`를 건드리지 않고 **내 소유 `_ensure_extras` 경로로만** 해소.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "팀장 서버에서 보면 내꺼도 보이냐는 말이야. 지금 내 페이지에는 내용이 없어서"
- 사용한 기법(있으면): (b 도구연동 — 프리뷰 MCP로 깨끗한 DB 재시드 후 라이브 스크린샷 검증)
- 결과: `routers/wiki.py` `_ensure_extras`에 멱등 데모 시드 추가 — 중앙 글(id 1·2·3)에 비어있을 때만 태그/👍 부여(SLURM·MPI·스토리지 등), 제목 중복 없을 때만 노하우 글 6건(GPU OOM·NCCL·Conda·/scratch·job array·점유 에티켓) + 데모 댓글 부착. `routers/chat.py`에는 messages 비었을 때만 데모 대화 4건 시드(점유 보드·위키 연계 맥락)하고 `get_messages`에서도 `_ensure_extras` 호출. **👍 시드값은 1로 캡**해 `test_helpful_increment_and_sort`(새 글 helpful=2가 최상단) 불변 유지 → **pytest 11 passed** 그대로. app.db 초기화 후 라이브 확인: 게시판 9글(태그 칩·도움순)·채팅 위젯 점유 보드 2건 + 대화 4건, 콘솔 오류 0. 통합본을 fresh clone해도 동일하게 재현(중앙 스키마/시드 불변).
- 막힘 → 해결: 세션 스코프 임시 DB(conftest)에서 시드 👍가 2 이상이면 정렬 테스트가 깨짐 → 모든 시드 helpful을 0~1로 제한해 테스트와 데모를 양립.

---

### [#12] L1 — 팀장 페이지(index·monitoring) 목업 포팅 + 실 API 배선
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: 빈 골격 페이지를 원본 목업 디자인으로 살리고 하드코딩 데이터를 실 API로 배선(B안). 모니터링에 3A 작업맥락 카드 + 등록 폼.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "다음 개발단계 진행할것." / "검토 결과 나오면 P1부터 고쳐줘"
- 사용한 기법: **(a) 서브에이전트 — 포팅 에이전트 + 독립 검토 에이전트** / (c) 재사용 산출물(원본 목업 재사용)
- 결과: `static/index.html`·`monitoring.html`을 `00_plan/dev_part/` 목업 디자인 유지한 채 포팅. 하드코딩 배열·가짜 jitter 제거 → `nodes/jobs/usage/latest` 3초 실폴링. 필드 매핑(`gpu`=사용률/`gpu_model`=모델), 상태 정규화(alloc→가동중/idle→유휴, RUNNING→실행중/PENDING→대기), KPI·Chart.js 실데이터. **3A 카드 작업맥락 + 등록 폼(POST→즉시 반영)**, 입력값 HTML 이스케이프(XSS 방지), 채팅 위젯 탑재, 네비 4A include 적용. 검토 에이전트 VERDICT=PASS(엔드포인트 200·POST→latest 라운드트립·pytest 5건). P1/P2 0건, P3 폴링 겹침은 setTimeout 체인으로 선조치, 테스트 행은 app.db 정리.
- 막힘 → 해결: 목업 필드명(`g`/`gpu`)이 API(`gpu`/`gpu_model`)와 달라 매핑 혼동 위험 → 샘플 실제값을 읽어 매핑 확정·검토로 재검증. 시각 렌더(픽셀) 확인은 `/browse` 또는 브라우저로 남김.

---

### [#13] 재사용 산출물 — PPT 자동생성 스킬 자작 + 디자인/접근성 스킬 3종 설치
- 작성자(팀원): 김민주(kimminju)
- 목표: 발표·IR·제안서 덱을 매번 손으로 만드는 반복작업을, "자료 1개 + 한 마디"로 일관된 .pptx까지 뽑는 **재사용 Claude Skill**로 자동화. 더불어 UI 품질·접근성 보조 스킬을 표준 자산으로 확보.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "ppt 스킬 추가해줘"
  > "https://www.ui-skills.com/ 여기서 디자인 스킬 ㄱㄱ"
- 사용한 기법(있으면): (c 재사용산출물 — `~/.claude/skills/` 자작 스킬) / (a 서브에이전트 — 빌드 후 QA 시각검토) / (b 도구연동 — python-pptx·markitdown·LibreOffice·poppler 파이프라인)
- 결과: **① kimminju-deck** — 첨부 가이드(145p PDF)·카탈로그(archetype 19·chart 70+)를 따라 `SKILL.md` + `references/` 9파일로 자작. `design-tokens.json`(5팔레트 SSOT) → `spec.json` → `VARIANT_TO_BUILDER` 라우팅 → `.pptx` 빌더(`build-template.py`, 14 variant 구현). 한글 폰트(Pretendard→Apple SD Gothic Neo) ea/cs 지정, 진행률 링은 네이티브 DOUGHNUT(holeSize 62)로 교체해 렌더러 호환 확보. QA러너(markitdown→soffice→pdftoppm→서브에이전트)로 8장 데모 전수 시각검증 PASS(한글 정상·온브랜드·금지패턴 0). **② baseline-ui / ③ fixing-accessibility** — ui-skills.com(github.com/ibelick/ui-skills, MIT)에서 설치. 세 스킬 전체를 `submit/assets/skills/`에 사본 보관.
- 막힘 → 해결: (1) `npx ui-skills` 외부 CLI 실행이 보안 분류기에 의해 차단 → 우회/강행하지 않고, 정적 `SKILL.md`만 GitHub raw에서 curl로 받아 **코드 실행 없이** 합법 설치. (2) 도넛 차트가 회색 단색으로 렌더(진행률 안 보임) → PIE/BLOCK_ARC 각도 방식 폐기, 네이티브 DOUGHNUT + per-point fill로 86% 인디고/14% 슬레이트 정상 표시. (3) 한글 zip 파일명 "Illegal byte sequence" → python zipfile로 basename 추출.

---

### [#14] 격리 샌드박스에서 디자인 리스타일(그린+사이드바+글라스 히어로) — 메인 무중단
- 작성자(팀원): 김민주(kimminju)
- 목표: 운영 중인 메인 서버(8000)를 건드리지 않고 **별도 격리 환경**에서 디자인을 실험·확정한 뒤, 마음에 드는 결과만 골라 반영. 기능·라우팅·텍스트·데이터·API는 절대 변경하지 않고 **시각(클래스/스타일)만** 손본다.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "테스트를 지금 내가 계속 했던 서버 말고 별도로 만들어서 하고 싶은데(혹시 혼동될까봐) 가능한가? 테스트해보고 마음에 드는 결과를 적용하고 싶음."
  > "기능/라우팅/텍스트/데이터/API는 절대 바꾸지 않는다. 시각만. 한 화면씩, 끝나면 보고."
  > "홈 화면에서 사내 HPC 포털 문구 젤 앞에 관련된 이모지 추가 … 이 상단 상자 디자인을 약간 투명한 느낌? mac os 느낌? 상단 상자는 정보공유·위키도 마찬가지 … 채팅 아이콘과 채팅창도 톤 통일"
- 사용한 기법(있으면): (b 도구연동 — Claude Preview MCP로 라이브 스크린샷·resize·eval 검증; 폴더 복사(rsync)+포트 8100+독립 app.db로 격리) / (a 서브에이전트 — 큰 리스타일 스펙을 화면별로 분할 실행)
- 결과: ① **격리 샌드박스 구축** — `hpc-portal-design-test/`로 복사, `.venv/bin/uvicorn main:app --app-dir … --port 8100` 단독 구동(메인 8000 무중단·별도 DB). ② **6화면 그린+사이드바 리스타일** — `theme.css` 단일 토큰 소스(그린 `#16b364` 팔레트, 레거시 `--blue/--navy/--orange` 재정의로 인라인 `var()` 자동 전환), 상단 네비 → 좌측 고정 사이드바(`_nav.html` 재작성·`include.js`에 모바일 햄버거 토글 추가), 카드 보더리스+섀도. 기능/텍스트/데이터/API 무변경. ③ **글라스 히어로** — 홈 "🖥️ 사내 HPC 포털" 이모지 추가 + 홈·위키 상단 박스를 반투명 유리(macOS 느낌: 반투명 그린 그라데이션 + `backdrop-filter:blur` + 흰 하이라이트/테두리)로. ④ **채팅 톤 통일** — `chat-widget.js`의 버튼·헤더를 히어로와 같은 그린 글라스 그라데이션으로(흰 글씨/아이콘). Preview 1280 데스크톱·모바일 반응형 모두 PASS.
- 막힘 → 해결: (1) 샌드박스 기동 "No module named uvicorn" → 메인이 쓰는 `.venv/bin/uvicorn`+`--app-dir`로 해결. (2) 프리뷰 기본 뷰포트 702px(≤760 모바일 분기)라 사이드바가 접힘 → `preview_resize` 명시 width 1280로 데스크톱 확인. (3) 프리뷰가 `chat-widget.js`를 캐시해 채팅 버튼이 파랑으로 보임 → curl로 서빙 파일이 초록(`rgba(22,179,100,…)`)·파랑(`1d4ed8`) 0건임을 확인하고, `?v=`+timestamp로 재주입해 실제 초록 톤 시각검증. **메인 반영은 사용자 지시에 따라 보류**("아직 반영하지말고 기록은 해줘").

---

### [#15] 브랜드 확정(GeoSR HPC 통합 포털) + 회사 로고 + 위키 히어로 정리 + 메인 반영
- 작성자(팀원): 김민주(kimminju)
- 목표: 샌드박스에서 확정한 디자인에 회사 정체성(브랜드명·로고)을 입히고, 잔여 장식을 정리한 뒤 **메인(8000)에 일괄 반영**.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "왼쪽 사이드바 아래부분에 회사로고 삽입가능?"
  > "정보공유 탭에 상단상자 오른쪽 부분 무늬있는거 없애줘. 홈 상단 상자랑 비슷하게 해줘"
  > "혹시 사내 HPC 포털말고 다른 멋진 이름 추천 가능? … 직관적으로" → 최종 채택: **"GeoSR HPC 통합 포털"**
  > "둘다" (= 로고 반영 + 메인 반영·로그)
- 사용한 기법(있으면): (b 도구연동 — Claude Preview MCP 라이브 검증, `sips`로 로고 메타 확인)
- 결과: ① **브랜드명 일괄 변경** — "사내 HPC 포털" → "GeoSR HPC 통합 포털"(사이드바 brand·홈 히어로 h1·5개 페이지 `<title>`·푸터). 기능/링크/데이터 무변경, 표시 텍스트만. ② **회사 로고** — `~/Downloads/ci/Geosr logo.png`(2362×1456, 투명배경) → `static/geosr-logo.png` 복사, `_nav.html` 사이드바 하단에 `.side-logo`(상단 구분선+폭 150px) 추가, 파일 없을 때 자동 숨김(`onerror`). ③ **위키 히어로 정리** — 우측 원형 무늬 2개(`:before/:after`) 제거 → 홈과 동일한 좌상단 유리 하이라이트만. ④ **이름 후보 브레인스토밍** — 컨셉형/관제형/직관형으로 제안, 사용자가 직관성 기준으로 "GeoSR HPC 통합 포털" 채택.
- 막힘 → 해결: (1) 붙여넣은 로고는 채팅 이미지라 파일 접근 불가 → 사이드바 자리/CSS 먼저 배선 후, `~/Downloads/ci/`에서 실제 PNG를 찾아 복사. (2) **메인 일괄 복사가 auto-mode 분류기에 차단** — 앞서 "아직 반영하지말고" 경계가 있어 "둘다"만으로는 메인 덮어쓰기 승인이 불명확하다고 판단(합리적 안전장치). → 사용자에게 명시적 재확인 요청, 승인 후 `hpc-portal-design-test/static`의 변경 10파일(8수정+신규 `theme.css`·`geosr-logo.png`)을 `hpc-portal/static`으로 반영. ※ 일부는 팀 소유 규칙상 팀장·팀원2 파일(`index/_nav/theme/monitoring/stats/system`)이라 통합 시 팀 조율 필요.

---

### [#16] 내 로컬 메인 반영 + 비파괴 디자인 통합 핸드오프 패키지(재사용 자산)
- 작성자(팀원): 김민주(kimminju)
- 목표: 확정 디자인을 내 로컬 통합앱(`hpc-portal/`, 개인 `kimminju` 브랜치)에 반영하고, **나중에 팀장이 통합할 때 다른 사람 파일(팀장 메인·정승명 브랜치)에도 안전하게 입힐 수 있는** 핸드오프 자산을 만든다.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "응 내꺼에 반영해주고(기록도 잘 하고 있지?? 채점에 들어가는거)."
  > "이 디자인을 나중에 팀장이 통합할 때 내꺼말고 그외것들(팀장 메인, 정승명 브랜치)에 적용될 수 있게 파일? 그런걸 만들어야할 것 같은데 어떻게 생각해?"
- 사용한 기법(있으면): (c 재사용산출물 — `submit/assets/design-system/` 드롭인+가이드+패치) / (b 도구연동 — git diff 패치 생성)
- 결과: ① **로컬 메인 반영** — 샌드박스 변경 10파일을 `hpc-portal/static/`에 복사, `diff -rq` 결과 ALL SYNCED. **커밋·푸시는 안 함**(원격/팀 main·타 팀원에 영향 0, 오직 내 `kimminju` 워킹트리). ② **통합 핸드오프 패키지** `submit/assets/design-system/` — 공유 드롭인 4개(`theme.css`·`_nav.html`·`include.js`·`geosr-logo.png`) + `DESIGN_HANDOFF.md`(3단계 적용법·페이지별 체크리스트·히어로 글라스 스니펫·Do/Don't) + `design-changes.patch`(8개 수정파일 `git apply`용). **핵심 설계 원리 명문화**: 디자인 ~80%가 `theme.css` 한 파일(토큰 재정의+전역 셀렉터+사이드바)에 집약 → 각 페이지는 `<link theme.css>` 한 줄만 추가하면 페이지 코드 무수정으로 그린+사이드바 자동 적용. **파일 통째 복사 금지**(타인 기능 유실 방지)를 가이드에 강조.
- 막힘 → 해결: "메인 반영"이 팀장 메인인지 내 브랜치인지 사용자 혼동 → `git branch`로 현재 `kimminju` 개인 브랜치 확인, 파일 복사는 로컬 워킹트리만 바꾸고 커밋·푸시 전까지 원격/팀에 무영향임을 설명 후 진행.

---

### [#17] 디자인 핸드오프 패키지 완비 — 필요 라이브러리 명시 + 신뢰 적용명령 + 내 영역만 분리
- 작성자(팀원): 김민주(kimminju)
- 목표: 8100 샌드박스 디자인을 **나중에 팀장이 전체 적용**할 수 있도록 필요한 파일·명령·라이브러리/스킬을 핸드오프 패키지에 빠짐없이 남긴다. 내 작업본은 **내 소유(wiki.html·chat-widget.js)만 남기고** 남의 페이지는 되돌린다.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "일단 내꺼만 적용해봐. 디자인 배치 이거 계속 수정할거임. 그리고 나중에는 이 디자인에 대한 걸 파일?로 만들어서 팀장이 나중에 통합할 때 전체 적용할 수 있도록 해야해."
  > "필요한 스킬이나 라이브러리 잇으면 그것도 명시하고"
- 사용한 기법(있으면): (c 재사용산출물 — `submit/assets/design-system/` 핸드오프 보강) / (b 도구연동 — `diff -q` 동기화 검증·`git apply --check` 패치 검증)
- 결과: ① **자산 동기화 검증** — 샌드박스(`hpc-portal-design-test/static/`) vs `submit/assets/design-system/`의 theme.css·_nav.html·include.js·로고 `diff -q` → 전부 동일. ② **필요 라이브러리/스킬 = 없음**을 `DESIGN_HANDOFF.md` §6에 표로 명문화: pip/npm/빌드/웹폰트/CDN/`@import` 전부 불필요(순수 CSS+시스템폰트+바닐라JS), 글라스는 네이티브 `backdrop-filter`, 차트는 기존 Chart.js 색만 변경, 적용에 스킬 불필요. ③ **패치 취약성 검증·문서화** — `git apply --check`를 origin/main 기준 실행 → 실패(스텁/브랜치 분리 상태에선 적용 불가). 따라서 §7에 **드롭인 4파일 복사 + 페이지별 `theme.css` 링크 한 줄**을 표준 명령으로 기재(비파괴, 페이지 내용 무관 동작). ④ **내 영역만 분리** — working tree에 남아있던 전체 적용 실험본 중 남의 페이지 4개(index·monitoring=팀장, stats·system=정승명)는 `git checkout`으로 되돌리고, 내 것(wiki.html·chat-widget.js)+공통 디자인 자산(theme.css·_nav.html·include.js·로고)만 유지.
- 막힘 → 해결: 처음엔 "내꺼만 적용"을 신규 코드 작성으로 오해해 서버추가 기능을 건드림 → 사용자가 "의견 공유만"이라 지적 → 즉시 `git checkout`으로 원복. 이후 working tree에 **이미 전체 디자인이 적용된 미커밋 실험본**이 있음을 발견 → "적용"이 아니라 "내 것만 남기고 분리"가 실제 작업임을 파악해 진행.

---

### [#18] 팀장 실서버 메인 머지 + 내 파트 실데모 호환 검증(노드명 하드코딩 0)
- 작성자(팀원): 김민주(kimminju)
- 목표: 팀장이 실서버 연동·모니터링 reframe를 메인에 올린 뒤, 내 브랜치로 `git pull`(머지)하고 **`TEAM_SYNC.md` 필수검토 3가지**(노드명 하드코딩 금지·GPU 없음·실행모드 mock/ingest)에 내 파트(위키·채팅 위젯)가 어긋나지 않는지 검증.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "팀장의 메인 브랜치가 업데이트 됐다고하거든? git pull 후 TEAM_SYNC.md 먼저 읽고 내 파트 진행해줘. 노드명 하드코딩하지말것(API대로 렌더) (hpc-portal/static/monitoring.html이 레퍼런스)"
- 사용한 기법(있으면): (b 도구연동 — git merge·curl 라이브 스모크·pytest) / (c 재사용산출물 — 머지 충돌 per-member 로그 분리)
- 결과: ① **`TEAM_SYNC.md` 선독** — 실클러스터는 `master,node1~13`(zero-pad 없음, GPU 0개), 모드별 노드집합 상이 → 라벨·카드·표를 API 응답대로 동적 생성하라(`monitoring.html`의 `fillNodeSelect()`/`map` 패턴)는 §2① 확인. ② **머지** — `origin/main`(팀장 #13~20: ingest 컬렉터·agent 스캔·CPU reframe) 머지, 충돌은 공유 `PROCESS_LOG.md` 1건뿐(소유 파일 분리 덕 코드 충돌 0). 팀장 로그는 별도 `team-d_LeeSeongHoo_PROCESS_LOG.md`로 들어와 있어 내 PROCESS_LOG는 HEAD(내 #13~17) 유지로 해소. ③ **내 파트 점검** — wiki.html은 노드 비의존(servers/posts만), chat-widget 점유보드는 **노드를 자유입력+API응답(`r.node`)으로 렌더**해 하드코딩 0 → mock·ingest 양쪽 무변경 동작. mock 모드 placeholder만 `예: node04`→`예: master, node3`로 모드중립화. ④ **라이브 검증(mock, 8011)** — `/api/wiki/servers`(3대)·`/posts`(9건)·`/chat/messages`(POST→GET)·`/chat/reservations`(node05 등록→목록 렌더) 200, wiki.html·chat-widget.js 200, pytest 11건 PASS.
- 막힘 → 해결: 머지 시 양 브랜치가 같은 `submit/PROCESS_LOG.md`에 #13~ 동시 추가해 충돌 → CLAUDE.md '개인별 영문 파일명' 규칙대로 팀장 로그는 이미 `team-d_LeeSeongHoo_PROCESS_LOG.md`로 보존됨을 확인하고, 공유 로그는 내 항목(HEAD)만 남겨 해소(정보 유실 0).

---

## 마무리 요약 (1~2줄)
- 가장 효과적이었던 에이전트 활용법: 프로토타입(디자인 자산)을 그대로 두고 **가짜 데이터만 API로 교체**해 1.5일 내 동작까지 도달 + 브라우저 MCP로 즉시 라이브 검증.
- 다른 팀이 그대로 따라 하려면 필요한 것: `submit/assets/`의 킥오프 프롬프트 + `dev_run.py` 단독 실행법(`uvicorn dev_run:app`) + 자체주입 위젯 패턴(한 줄 로드).
