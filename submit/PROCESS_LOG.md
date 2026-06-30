# PROCESS_LOG — 작업 기록 (과정 70점의 핵심 근거)

> 원칙: **실제로 시킨 프롬프트를 그대로 인용**할 것. 요약만 있으면 점수가 깎입니다.

## 작성자 정보 (개인별 로그 — 본인 것만)
- 팀명: team-d
- 본인 이름(작성자): 정승명 (jeongseungmyong)
- 공통과제(우리 팀이 자동화한 반복 수작업): HPC 사용자들이 **노드 사용 현황·서버 환경·노하우를 메신저/구두/개별 문의로 매번 확인·조율**하던 것 → 사내 HPC 통합 포털로 한곳에 모음.
- 내가 맡은 부분: **팀원2** — **사용량 통계(stats)** + **시스템 상태(system)** 페이지. 노드별 온도·디스크·NFS(+GPU온도·메모리) 점검과 노드별/사용자별 GPU 사용량 집계·추이.
- 자유과제(있으면): -

> 제출 시 영문 파일명 `team-d_jeongseungmyong_PROCESS_LOG.md`로 저장(이 파일과 동일 내용). 한글 이름은 위 작성자 정보에만.

## 효과 측정 (Before → After)
> 상세는 `BEFORE_AFTER.md`. 내 파트(시스템 상태·사용량 통계) 기준.

| 지표 | Before(기존 수작업) | After(에이전트화) |
|------|------|------|
| 사용량 집계 | **정형화된 절차 없음** — 매월 1일 기준 해당일까지의 정보를 수기 집계하고 **월말에 집계를 기록**(주기적 수작업, 실시간성 없음) | `stats.html`에서 노드별/사용자별/추이를 **상시 자동 집계**(차트), 언제든 현재 시점 확인 |
| 노드 상태 점검(온도·디스크·NFS) | 정형화된 점검 절차 없이 필요 시 개별 확인 | `system.html` 한 화면에서 8노드 색상(green/orange/red) 점검 + 2.5초 자동 갱신 |
| 화면 개발 | 새로 디자인·코딩 | 기존 목업의 디자인 토큰·Chart.js·카드/폴링 패턴 재사용으로 가속 |

## 사용 기법 (권장·가점)
- [x] (a) 서브에이전트 / 역할 분담 — 기존 목업 디자인 패턴 추출을 **Explore 에이전트 2개 병렬**로 수행(모니터링/인덱스, 위키/채팅).
- [x] (b) 외부 도구·데이터 연동 — git pull/push로 최신 main 동기화 및 브랜치(`jeongseungmyong`) 작업.
- [x] (c) 재사용 산출물 — `DEV_BLUEPRINT.md`의 디자인 토큰·노드 카드·Chart.js 초기화 패턴 재사용 + 작업 계획 문서(체크목록/방법/시각화/추가계획).

---

## 작업 로그 (단계마다 1개씩 누적 / 시간순)

### [#1] 최신 main 동기화 + 프로젝트 청사진 숙지
- 작성자(팀원): 정승명 (팀원2)
- 목표: 팀장이 새로 올린 main(역할 개편·DEV_BLUEPRINT)을 받아 내 담당 범위를 정확히 파악.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "새로 업로드된 main 브랜치를 가져와서 숙지해요."
  > "나는 jeongseungmyong이다. 브랜치도 jeongseungmyong이다. 팀원 2이다."
- 사용한 기법: (b) git — `main` 최신화(`53b9acc..7ab04fc`) 후 `jeongseungmyong` 브랜치를 최신 main으로 정렬·푸시.
- 결과: 역할 개편(3페이지→5페이지) 확인. 팀원2 = 사용량 통계 + 시스템 상태, 소유 파일(routers/stats·system.py, static/stats·system.html, data/sample_health.txt)과 통합 철칙(노드 `node01~08`, 채팅 위젯 한 줄 로드) 숙지.
- 막힘 → 해결: 로컬에 같은 이름 폴더가 있어 `git clone` 실패 → 이미 클론된 동일 origin임을 확인, clone 대신 pull/브랜치 정렬로 처리.

### [#2] plan mode 인터뷰로 팀원2 작업 계획 확정
- 작성자(팀원): 정승명 (팀원2)
- 목표: 코딩 전 "무엇을·어떻게 체크하고 어떻게 시각화할지"를 계획으로 먼저 확정.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "전반적 계획 - 체크 목록 - 체크 방법 - 체크 목록 시각화 방법 - 추가될 수 있는 계획"
- 사용한 기법: (a) Explore 서브에이전트 2개로 기존 목업 디자인 패턴 추출 / (c) 재사용 산출물
- 결과: 인터뷰로 3가지 결정 확정 — ①범위=두 페이지 모두 ②핵심 체크항목=온도·디스크·NFS+GPU온도·메모리 ③갱신=자동 폴링(2~3초). 계획 문서에 체크목록/체크방법/시각화/추가계획 정리. 재사용 자산(디자인 토큰·노드카드·Chart.js·폴링 패턴) 식별.
- 막힘 → 해결: 채점용 개인 로그가 팀장 것으로 채워져 있어, 내 개인 로그로 분리 필요 확인.

### [#3] 사용량 통계 + 시스템 상태 구현 및 로컬 단독 검증
- 작성자(팀원): 정승명 (팀원2)
- 목표: 소유 파일만으로 두 페이지를 만들고, 다른 사람 코드 없이 `/docs`에서 단독 동작 검증.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > (계획 승인 후) 체크목록/체크방법/시각화 계획대로 sample_health.txt·routers·static 구현 진행
- 사용한 기법: (c) 디자인 토큰·Chart.js 초기화·카드/폴링 패턴 재사용
- 결과:
  - `data/sample_health.txt` (node01~08, temp/gpu_temp/mem/disk/nfs 한 줄 형식, green/orange/red 분포).
  - `routers/system.py` — `node_health` 테이블 IF NOT EXISTS + 시작 시 파싱 적재, `GET /api/system/health`. 통합 시 팀장 `db.py` 자동 사용, 없으면 로컬 폴백(독립 동작).
  - `routers/stats.py` — `usage_log` 자체 시드(Random(42) 재현성), `GET /api/stats/usage`(byNode/byUser/trend).
  - `static/system.html` — KPI(정상/주의/위험/최고온도) + 노드 카드(게이지 바 + 디스크/NFS 칩 + 종합 롤업 배지) + 2.5초 폴링.
  - `static/stats.html` — KPI + Chart.js 4.4.1 차트 3개(노드별 막대·사용자별 순위·일자별 추이) + 30초 갱신. 두 페이지 모두 채팅 위젯 `<script>` 한 줄 포함.
  - 검증: 임시 하니스(TestClient)로 `GET /api/system/health`(200, 8노드)·`GET /api/stats/usage`(200, 집계) 단독 응답, `/openapi.json` 두 경로 등록(=`/docs` 정상), static 페이지 200 서빙 확인.
- 막힘 → 해결: ① 시스템의 `python`이 깨진 Store 스텁 → 실제 런처 `py`(3.14.2)로 전환. ② fastapi 미설치 → `py -m pip install fastapi uvicorn httpx`로 설치 후 검증. ③ SQLite `ON CONFLICT` 호환성 고려해 `INSERT OR REPLACE` 사용.

### [#4] 추가기능 구현 — 위험 알림 배너 + 위험만 보기 필터 + 평균 온도 추이 차트
- 작성자(팀원): 정승명 (팀원2)
- 목표: 코어 완성 후 운영 가시성·가점용 추가 기능을 자기완결형으로 구현.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "위험 알림 배너 + 위험만 보기 필터, 상태 이력 추이 차트" (추가계획 '3번' 착수)
- 사용한 기법: (c) Chart.js 라인차트·디자인 토큰 재사용
- 결과:
  - `routers/system.py`: `health_history` 테이블 + 과거 30스냅샷 시드 + 폴링 시 20초 간격 기록, `GET /api/system/history`(시점별 평균 CPU/GPU 온도 시계열).
  - `static/system.html`: 🚨 **위험 알림 배너**(위험 노드 나열), **전체/주의 이상/위험만 필터**(클라이언트), **평균 온도 추이 라인차트**(20초 갱신). 등급 계산을 공통 헬퍼 `overallOf`로 일원화(카드·KPI·필터·배너 공유).
  - 검증: `GET /api/system/history` 200 응답, Edge 헤드리스 스크린샷으로 배너·추이 차트·필터 렌더 확인.
- 막힘 → 해결: 카드/KPI/필터/배너가 각자 등급 계산해 중복 → `overallOf(n)` 헬퍼로 통합해 일관성 확보.

### [#5] 사용량 통계 보강 — 요약 KPI + 사용자 비중 도넛 + 노드별 사용자 구성 스택
- 작성자(팀원): 정승명 (팀원2)
- 목표: 사용량 통계 페이지에 통계치를 더 얹어 분석 깊이·임팩트 강화.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "용량 통계치 추가 적용"
- 사용한 기법: (c) Chart.js(도넛·스택 막대) 재사용
- 결과:
  - `routers/stats.py`: `GET /api/stats/usage` 응답에 **summary**(총·일평균·최번일·peakHours·활성 사용자/노드·일수)와 **stacked**(노드×사용자 구성) 추가.
  - `static/stats.html`: KPI 3→**6종**(총/일평균/최번일/최다 사용자/활성 사용자/사용 노드), **사용자 사용량 비중 도넛**, **노드별 사용자 구성 스택 막대** 신규(기존 3차트 + 2차트 = 5차트). 8색 팔레트 공통화.
  - 검증: `GET /api/stats/usage`에 summary·stacked 포함(200), Edge 헤드리스 스크린샷으로 KPI 6종·도넛·스택 렌더 확인.
- 막힘 → 해결: KPI 타일 수 증가로 3열 고정이 좁아짐 → `repeat(auto-fit,minmax(150px,1fr))`로 자동 줄바꿈 처리.

---

### [#6] 개발 사양서(SPEC) 작성·저장
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: 코딩 착수 전, 블루프린트를 정식 개발 사양서 형식(기능/비기능 요구사항·DB·API 스키마·검수 기준)으로 구조화해 팀 공용 기준 문서 확보.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "지금 프로젝트의 개발 사양서를 작성하고 저장할것."
- 사용한 기법: (c) 재사용 산출물 — `DEV_BLUEPRINT.md`를 단일 진실 공급원으로 삼아 SPEC 파생
- 결과: `00_plan/SPEC.md` 작성(12장: 개요·시스템개요·FR/NFR·아키텍처·DB스키마·API사양·UI토큰·통합·빌드계획·검수기준·제약). 제출 자산으로 `submit/assets/SPEC.md` 사본 저장, `submit/evidence/timestamps.txt`에 수정시각 기록.
- 막힘 → 해결: 루트 `CLAUDE.md`(해커톤 규칙)는 보존해야 해 사양은 별도 문서로 분리. 블루프린트와 충돌 시 블루프린트 우선 명시.

---

### [#7] AGENTS.md 존재 확인 및 보존
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: 저장소 기여자 가이드 생성 요청을 처리하되, 기존 `AGENTS.md`가 있으면 수정하지 않는 조건 준수.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "Generate a file named AGENTS.md ... Before writing, check whether AGENTS.md already exists ... If it does, do not overwrite or modify it."
- 사용한 기법: (b) 도구연동 — `rg --files`, `ls`, `git log`로 파일 존재와 저장소 상태 확인
- 결과: 루트에 `AGENTS.md`가 이미 있음을 확인해 파일을 생성·수정하지 않음. 기존 가이드는 보존.
- 막힘 → 해결: 요청 조건과 기존 파일 존재가 충돌 → "수정 금지" 조건을 우선 적용.

---

### [#8] 개발 사양서 내용 검토
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: `00_plan/SPEC.md`가 확정 청사진(`DEV_BLUEPRINT.md`)과 충돌하지 않고 구현 착수 기준으로 충분한지 점검.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "지금 개발 사양서 내용 검토해봐"
- 사용한 기법: (c) 재사용 산출물 — `DEV_BLUEPRINT.md`를 기준 문서로 대조 검토
- 결과: 전체 구조·역할·DB·API·통합 방향은 적합. 보완 권고: 위젯-모니터링 반영 관계 명확화, HTTP 상태코드 일관화, `id INTEGER PRIMARY KEY AUTOINCREMENT` 등 SQLite DDL 구체화, 샘플 파일 포맷 예시 추가.
- 막힘 → 해결: -

---

### [#9] mpirun 직접 실행 작업 및 SPEC 보완사항 반영
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: `squeue`/PBS 큐에 잡히지 않는 `mpirun` 직접 실행 작업도 포털 설계에 포함하고, 검토 보완사항을 문서에 반영.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "squeue나 pbs를 안쓰고 그냥 mpirun으로 던지는 작업도 있는데, 이런것도 고려가 되는거임?"
  > "해당 계획 및 보완사항까지 반영해서 수정 및 보완"
- 사용한 기법: (c) 재사용 산출물 — `DEV_BLUEPRINT.md`와 `SPEC.md` 동시 보정, `submit/assets/` 사본 갱신
- 결과: `mpirun` 직접 실행 작업은 자동 탐지 대신 `node_usage` 수동 등록(`source=mpirun/manual`)으로 커버한다고 명시. `node_usage.source` 필드 추가, POST 입력 `{source?}` 보완, 성공 HTTP 200 통일, SQLite DDL 구체화, `sample_squeue/sinfo/health` 포맷 예시 추가.
- 막힘 → 해결: 실서버 `ps`/`nvidia-smi`/PBS 파싱까지 넓히면 구현 리스크가 커짐 → 해커톤 범위는 수동 맥락 등록으로 제한하고 향후 확장으로 분리.

---

### [#10] 엔지니어링 검토(/plan-eng-review) — 설계 잠금 6건
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: 코딩 착수 전, 설계 문서(DEV_BLUEPRINT·SPEC)를 아키텍처·코드품질·테스트·성능 관점에서 검토해 결함을 잠그기.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "/plan-eng-review" (검토 대상: 설계 문서)
- 사용한 기법: (a) 스킬 활용 `/plan-eng-review` 인터랙티브 검토 / (c) 재사용 산출물 SPEC·BLUEPRINT 갱신
- 결과: 이슈 6건 합의·채택 — **1A** db.py 동시성(WAL+busy_timeout+요청별 연결, `database is locked` 차단), **2A** 멱등 시드/스키마(`--reload` 재부팅 안전), **3A** node_usage 노드별 최신 1건 표시, **4A** `_nav.html` JS 자가주입+pathname active(DRY), **5A** 파서 입력 가드(부팅 무중단), **6A** pytest 최소 세트(파서·멱등시드·node키정합·TestClient 200). 추가 T7(채팅 LIMIT)·T8(노드키 상수화). `SPEC.md §13`·`DEV_BLUEPRINT §14`에 반영, `submit/assets/` 사본 갱신. VERDICT: ENG REVIEW CLEARED, 미해결 0건.
- 막힘 → 해결: 복잡도 게이트(13파일>8)는 과설계가 아니라 3인 분담 결과로 판단 → 현 범위 유지. 검토 결정 5/6이 팀장 공통 뼈대에 모여, 병렬 착수 전 선반영하기로.

---

## 마무리 요약 (1~2줄)
- 가장 효과적이었던 에이전트 활용법: **계획(체크목록/방법/시각화)을 먼저 확정**하고 기존 목업의 디자인 자산을 재사용해, 소유 파일만으로 충돌 없이 두 페이지를 빠르게 구현·단독 검증.
- 다른 팀원이 그대로 따라 하려면 필요한 것: DEV_BLUEPRINT의 소유 파일 경계 + 라우터의 "자체 테이블/시드 + 팀장 db.py 자동 폴백" 패턴(통합 전에도 `/docs` 단독 동작).
