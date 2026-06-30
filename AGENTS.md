# 예보사업부 AI·AX 해커톤 — 작업 규칙 (이 파일은 자동 로드됩니다)

너는 이 해커톤 참가팀의 개발을 돕는 에이전트다. 아래 규칙을 끝까지 지켜라.

## 제출 폴더 (가장 중요)
이 프로젝트에는 이미 `submit/` 폴더가 있다. **모든 제출물을 반드시 그 안에 저장·갱신**하라.
- 작업 기록 → `submit/PROCESS_LOG.md`
- Before/After(효과 측정) → `submit/BEFORE_AFTER.md`
- 재사용 자산(프롬프트/스킬/CLAUDE.md 사본 등) → `submit/assets/`
- 증빙(자동 timestamps / 선택적 세션 export) → `submit/evidence/`

`submit/` 폴더나 위 파일이 없으면 **네가 만들어라.** 개발한 코드/산출물은 프로젝트 루트(또는 `src/`)에 자유롭게 둬도 된다(제출 시 폴더 전체를 압축한다).

## 채점 방식 (중요)
- 과정 70 : 결과 30. **과정은 `submit/PROCESS_LOG.md`를 근거로 AI가 객관 채점**한다. (수작업 증빙 불필요)
- 로그를 성실하고 구체적으로 남기는 것이 곧 점수다. (입문자는 처음에 비어도 괜찮다 — Day1 13:30 운영자 중간점검 때 보정하면 된다.)

## 세션을 시작할 때 (맨 처음 1회, 네가 먼저 물어라)
- 사용자에게 **① 팀명 ② 본인 이름 ③ 자동화할 반복 수작업(공통과제)**을 한 번 물어 `submit/PROCESS_LOG.md`의 '작성자 정보'에 적어라. (이미 채워져 있으면 건너뛴다.)
  **팀원 전원 이름은 묻지 마라** — 각자 본인 PC·본인 계정으로 따로 작업하고, **개인별로 로그를 작성·제출**한다(팀별로 모아 채점).
- 이어서 규칙 8대로 **기존 방식(Before)**도 한 번 물어 `submit/BEFORE_AFTER.md`에 적어 둔다.
- 사용자가 한꺼번에 다 모르면 아는 것만 적고 나머지는 작업 중 채운다. **단, 사용자가 직접 타이핑하게 두지 말고 네가 물어서 대신 적어라.**
- 팀명·이름을 알면, 제출용으로 `submit/PROCESS_LOG.md`를 **영문(로마자) 파일명** `<팀영문명>_<이름로마자>_PROCESS_LOG.md`로 저장(또는 세션 끝에 그 이름으로 복사)해라. 예: `teamA_kim_PROCESS_LOG.md`. **한글 파일명은 쓰지 마라**(압축 시 깨짐) — 한글 팀명·이름은 파일 안 '작성자 정보'에 적는다. 팀별로 개인 로그가 충돌 없이 모인다.

## 반드시 지킬 것
1. 작업은 에이전트 주도로 진행한다(단순 검색 말고 실제로 만들게 한다).
2. **의미 있는 단계가 끝날 때마다 `submit/PROCESS_LOG.md`에 항목 1개를 append** 하라. 사용자가 잊으면 네가 먼저 "방금 작업을 로그에 남길까요?"라고 챙겨라.
3. 로그에는 실제 지시/프롬프트의 **핵심 문장을 그대로 인용**한다(두루뭉술한 요약 금지).
4. 각 로그 항목에 **작업한 팀원 이름**을 표시한다(전원 참여가 보이도록).
5. **타임스탬프 증빙은 네가 자동으로 남겨라**: 산출물 파일 수정 시각을 `submit/evidence/timestamps.txt`로 정리해 둔다. (세션 export가 쉬운 도구면 함께 두면 좋다 — 선택.) **화면 캡처 같은 수작업 증빙은 사용자에게 시키지 마라.** 무임승차 검증은 Day2 미니시연으로 한다.
6. 민감자료(미공개 관측 원본·개인정보·대외비)는 외부에 올리지 말고 마스킹/익명화한다.
7. 제출 파일명은 영문 권장(한글 파일명은 일부 압축 도구에서 깨진다).
8. **효과 기록(자동)**: 주제가 정해지면 사용자에게 "이 일을 기존엔 어떻게/얼마나 들여 했는지" 한 번 물어 `submit/BEFORE_AFTER.md`의 Before로 적고, 작업하며 After·효과를 채워라. **효과 지표는 업무에 맞게 자유**(시간·반복횟수·자료 수·품질·일관성·오류 등 해당되는 것; 정량이 어려우면 정성). 특정 지표를 강요하지 마라.

## (권장 — 잘 쓰면 가산점, 필수 아님)
- 서브에이전트(역할분담) / 외부 도구·데이터 연동 / 재사용 산출물(스킬·프롬프트·CLAUDE.md)을 쓰면 활용 점수(①)에 **가산점**. 못 써도 불이익 없음 — 팀의 경험자와 함께 실습하며 시도하라.

## PROCESS_LOG 항목 형식 (이 형식 그대로 append)
---
### [#순번] {짧은 제목}
- 작성자(팀원):
- 목표:
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "(실제로 입력한 지시/프롬프트의 핵심 문장)"
- 사용한 기법(있으면): (a 서브에이전트 / b 도구연동 / c 재사용산출물)
- 결과:
- 막힘 → 해결(있었다면):
---

## 세션을 마칠 때
- `submit/CHECKLIST.md`를 보고 **빠진 제출물을 사용자에게 알려라.** 사용자가 "제출 점검해줘"라고 하면 체크리스트 기준으로 점검 결과를 표로 보여줘라.

---
---

# HPC 포털 — 프로젝트 기술 문서

> 위(여기까지)는 **해커톤 운영 규칙**이고, 아래는 루트에서 앱을 개발할 때 함께 적용되는 **HPC 포털 프로젝트의 기술 문서**다. 원본은 `00_plan/CLAUDE.md`이며 둘은 동일하게 유지한다. 둘 다 적용된다.

## 단일 진실 공급원 (먼저 읽을 것)
`00_plan/DEV_BLUEPRINT.md` 가 이 프로젝트의 **확정 스펙**이다. 역할·페이지·소유 파일·DB·API 구성은 이 문서가 기준이며, 더 오래된 `00_plan/HPC포털_개발_핸드오버.md`의 같은 항목을 **대체**한다(핸드오버는 일반 원칙만 유효). 아래 요약과 충돌하면 `DEV_BLUEPRINT.md`가 우선한다. 새 작업 전 §2(역할)·§4(DB)·§6(API)·§7(통합 접점)을 확인하라.

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
- 존재하는 것은 **정적 HTML 목업뿐**(API 연동 없는 디자인 프로토타입): `00_plan/dev_part/{index,monitoring}.html`(팀장), `00_plan/userA_part/wiki.html`(팀원1), `00_plan/userB_part/chat.html`(팀원2 목업 → 본 개발 시 팀원1의 `chat-widget.js`로 흡수). 본 개발 시 `static/`로 옮겨 `fetch` 배선한다.
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
