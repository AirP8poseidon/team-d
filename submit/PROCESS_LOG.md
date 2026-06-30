# PROCESS_LOG — 작업 기록 (과정 70점의 핵심 근거)

> 원칙: **실제로 시킨 프롬프트를 그대로 인용**할 것. 요약만 있으면 점수가 깎입니다.

## 작성자 정보 (개인별 로그 — 본인 것만)
- 팀명: team-d
- 본인 이름(작성자): LeeSeongHoo (이성호)
- 공통과제(우리 팀이 자동화한 반복 수작업): HPC 사용자들이 **노드 사용 현황·서버 환경·노하우를 메신저/구두/개별 문의로 매번 확인·조율**하던 것 → 사내 HPC 통합 포털로 한곳에 모음 (SLURM 숫자 위에 사람의 맥락 + 실시간 소통 + 운영 가시성).
- 내가 맡은 부분: **팀장** — 공통 뼈대(FastAPI/SQLite/공통 CSS·네비) + 모니터링 페이지(CPU/GPU + node_usage "누가·왜" 맥락) + 막판 통합.
- 자유과제(있으면): -

> 제출 시 영문 파일명 `team-d_LeeSeongHoo_PROCESS_LOG.md`로 저장(이 파일과 동일 내용). 한글 이름은 위 작성자 정보에만.

## 효과 측정 (Before → After)
> 상세는 `BEFORE_AFTER.md`. 정량 지표는 구현 라운드(동작물 완성 후)에 채움. 현재(설계·핸드오버 단계)까지의 효과는 아래.

| 지표 | Before(기존 수작업) | After(에이전트화) |
|------|------|------|
| 설계·합의 산출물 정리 | 구두 합의 + 흩어진 메모, 새 세션마다 재설명 | 인터뷰 1회로 청사진 1문서 확정(역할·DB·API·통합 접점) |
| 팀원 착수 준비 | 각자 무엇을·어떻게 할지 말로 전달, 경계 모호 | 자기완결 핸드오버 2종 + 붙여넣기용 킥오프 프롬프트 → 받아서 바로 시작 |
| 파일 충돌 위험 | 같은 파일 동시 수정 우려 | 소유 파일 분리 명문화(충돌 0 설계) |

## 사용 기법 (권장·가점)
- [ ] (a) 서브에이전트 / 역할 분담  ← 이번 세션 미사용(직접 작업)
- [x] (b) 외부 도구·데이터 연동 — git 커밋/푸시로 팀 공유
- [x] (c) 재사용 산출물 — `DEV_BLUEPRINT.md`, 팀원별 핸드오버+킥오프 프롬프트, 프로젝트 `CLAUDE.md`

---

## 작업 로그 (단계마다 1개씩 누적 / 시간순)

### [#1] 인터뷰 방식으로 프로젝트 청사진 설계 착수 (plan mode)
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: 코딩 전에 개발 계획·방법·청사진을 인터뷰로 먼저 확정.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "지금 계획된 내용을 검토하려고 함. 인터뷰 스킬 적용해서 프로젝트 개발 계획, 방법, 청사진 계획 먼저 작업하자"
- 사용한 기법: (c) — 기존 핸드오버 문서를 단일 진실 공급원으로 활용
- 결과: 범위(공통뼈대+모니터링=팀장)·1차 산출물(청사진 문서 먼저)을 인터뷰로 확정. plan 파일에 청사진 초안 작성.
- 막힘 → 해결: -

### [#2] 구현 방식 결정 — HTML 목업 vs API+SQL 장단점 브리핑
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: 정적 목업으로 갈지, FastAPI+SQLite로 실제 배선할지 근거 있는 결정.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "html 목업이 좋을지, api+spl 연결이 좋을지 각각의 장단점 브리핑"
- 사용한 기법: -
- 결과: **B안 채택** — 기존 목업 재사용 + 실제 API/SQLite 배선. 근거: 제품 하이라이트인 "라이브 데이터 흐름(채팅 등록→모니터링 반영)"은 공유 상태(DB) 없이는 위조라, 채점의 동작 완성도·임팩트(27점)를 못 살림.
- 막힘 → 해결: -

### [#3] 역할·페이지 구성 개편
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: 초기 3분담(모니터링/위키/채팅)을 실제 팀 구성에 맞게 재설계.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "팀원1은 정보공유, 실시간 채팅 담당이고, 채팅은 별도 페이지 말고 숨김 오픈 기능 있는 플로팅 창 같은걸로 구성하고 싶음. 팀원 2는 새롭게 사용량 통계 페이지 만들것임 … 서버 온도, 하드 연결, nfs 연결상태 등 cpu, gpu 사용량 말고도 확인해야하는 정보 모니터링 페이지도 별도 추가 -> 이 내용은 팀원2가 담당."
- 사용한 기법: -
- 결과: 5페이지 구성 확정 — 팀장(index/monitoring), 팀원1(위키 + **채팅 플로팅 위젯**), 팀원2(**사용량 통계 + 시스템 상태** 신설). 인터뷰로 두 결정 추가 확정: ① 채팅 공유는 자체 주입 위젯(`chat-widget.js` 한 줄 로드), ② "누가·왜" 맥락(node_usage)은 팀장 모니터링에 유지.
- 막힘 → 해결: 여러 페이지에 뜨는 채팅이 "각자 자기 파일만 수정" 원칙을 깰 위험 → 자체 주입형 위젯(팀원1 단독 소유 + 타 페이지는 script 한 줄)으로 해결.

### [#4] 청사진 문서화 + 라이브러리·유용 스킬 정리
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: 확정 내용을 팀 공유용 문서로 + 본 개발 의존성/도구 정리.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "이제 계획에 본 개발에 필요한 라이브러리 목록, 사용하면 유용한 스킬 내용 작성"
- 사용한 기법: (c) — 재사용 산출물 `DEV_BLUEPRINT.md`
- 결과: `00_plan/DEV_BLUEPRINT.md` 작성(역할·DB·API·통합 접점·시연 시나리오·킥오프 프롬프트). §12 라이브러리(백엔드 `fastapi`+`uvicorn[standard]`만, 프론트 Chart.js CDN+바닐라, 재현성용 버전 핀), §13 단계별 유용 스킬(`/run` `/investigate` `/verify` `/browse` `/qa` `/design-review` `/code-review` `/diagram` `/make-pdf` 등) 추가. `submit/assets/`에 사본.
- 막힘 → 해결: 목업의 외부 의존성 확인(grep) → Chart.js 4.4.1 단일 CDN만 사용함을 검증해 의존성 목록 확정.

### [#5] 팀원1·2 핸드오버 작성 + git 공유(커밋·푸시)
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: 팀원이 받아 바로 자기 세션에서 착수할 자기완결 문서화 후 git 공유.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "이제 각자 팀원1, 팀원2에게 핸드오퍼 할 내용 정리하고 git으로 다시 공유할거임."
  > "이제 커밋+푸시할것"
- 사용한 기법: (b) git 연동 / (c) 재사용 산출물(핸드오버·킥오프 프롬프트)
- 결과: `00_plan/handover/`에 `member1_wiki_chat.md`·`member2_stats_system.md`·`README.md`(팀장 통합 체크) 작성. `.gitignore`에 `.DS_Store` 추가. origin/main에 커밋·푸시(`53b9acc..314b904`) → 팀원이 `git pull`로 수령.
- 막힘 → 해결: `submit/`는 gitignore라 git 공유 안 됨을 확인 → 팀 공유용 문서는 추적되는 `00_plan/`에 두고, submit엔 제출용 사본만 유지하도록 분리.

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

### [#11] 서브에이전트로 공통 뼈대 스캐폴딩 + 독립 검토 에이전트 + 수집 심(collector)
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: 공통 뼈대(FastAPI/SQLite + 잠금결정 6건)를 서브에이전트로 짓고, 별도 검토 에이전트로 적대적 검증. 실서버 연동 대비 정보수집 체계(collector 심)도 함께.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "서브에이전트 불러와서 공통 뼈대 스캐폴딩 시작해줘, 그리고 결과 검토하는 에이전트 만들어줘. 그리고 실제로 서버와 연동할 정보수집 체계도 만들어줘야할거같음. 실제 서버 연동은 어떤식으로 함?"
- 사용한 기법: **(a) 서브에이전트 2개 — 스캐폴딩 에이전트 + 독립 검토 에이전트** / (c) 재사용 산출물 SPEC 기준
- 결과: `hpc-portal/` 생성(db.py·main.py·routers×5·static·data·tests·requirements). 결정 1A(WAL+busy_timeout 요청별 연결)·2A(멱등 시드, collector는 INSERT OR REPLACE)·3A(/usage/latest 노드별 최신1건)·4A(include.js nav 자가주입)·5A(파서 가드)·6A(pytest 5건)·T7(채팅 LIMIT50)·T8(NODES 상수) 전부 구현. **수집 심**: `collectors/{base,mock,slurm,prometheus}.py` + 5초 백그라운드 주기 갱신 → 목업 동작, 실연동은 slurm.py 드롭인. 실서버 연동 방식 정리: DB=읽기모델이라 writer만 교체(① 온클러스터 squeue/sinfo/nvidia-smi subprocess ② Prometheus API 쿼리 ③ 푸시형 데몬). 검토 에이전트 VERDICT=PASS(2번째 갱신 틱 idempotent·파서 무중단 실측), P3 1건(선행 빈 줄→헤더가 데이터로 먹히는 잠복 버그) 발견 → 헤더를 '첫 비어있지 않은 줄'로 skip하게 수정, 회귀 프로브 통과. SPEC §7.1을 코드(추가 source 필드·/usage/latest)에 맞춰 갱신.
- 막힘 → 해결: 실연동 범위가 모호(목업 vs 실수집기) → 수집 심만 지금 구축(A)으로 잠가 데모 안전 + 실연동 준비. 파서 P3는 5A 보장을 깨므로 잠복이어도 즉시 수정.

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

### [#13] 실서버 연동 — push형 수집(ingest) + 노드 에이전트 + SSH 수신
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: 각 계산 서버가 자기 정보를 SSH로 워크스테이션(포털)에 밀어넣고 대시보드가 조회하는 push형 수집 체계 구축.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "각자 서버에서 필요한 정보를 ssh로 웹서비스 서버로 넘겨줘서 조회할 수 있게 하고싶음"
  > "임시로 여기 서버 아이피 할당해서 연결해서 넘겨받고 싶은데. 방법은?"
- 사용한 기법: (b) 도구·OS 연동(SSH/scp, nvidia-smi/df/ps), (c) 재사용 산출물(collector 심)
- 결과: **수신** `collectors/ingest.py`(+팩토리 `ingest` 등록) — `data/incoming/<node>.json` 읽어 nodes/jobs/health upsert, 깨진 파일·빈 폴더 무시, **유효 리포트 0개면 mock 폴백**(데모 안전), node01~08만 수용. **송신** `agent/node_report.py` — nvidia-smi/CPU/MEM/df/NFS/`ps`(mpirun 직접 실행) 수집 → JSON → scp 푸시(1회/루프/--out 테스트). `agent/README.md` 설정 안내. 포털 호스트 SSH(원격 로그인) ON 확인(10.10.9.101 sshd 응답). **오프라인 검증**: 에이전트로 리포트 생성→incoming 투입→`COLLECTOR=ingest` 부팅→node04(A100 gpu91·temp71)·mpirun 작업이 대시보드 API에 반영 확인. `data/incoming/*.json`은 gitignore(.gitkeep로 폴더 유지), pytest 5건 유지.
- 막힘 → 해결: ① macOS `systemsetup -setremotelogin`이 Full Disk Access 요구 → GUI(공유→원격 로그인)로 우회. ② `lsof`가 root 소유 22번 소켓을 비권한으로 못 봐 OFF 오인 → ssh BatchMode 핸드셰이크로 확정. ③ 에이전트 mpirun 탐지가 인자 문자열 부분일치로 오탐(P2) → 실행파일명이 정확히 mpirun/mpiexec인 토큰만 매칭하도록 수정·재검증.

---

### [#14] 실서버 적용 전 — 서버 제원 정찰 스크립트
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: 가정(nvidia-smi·/proc·nfsstat 등)이 실서버와 맞는지 모르므로, 적용 전에 각 서버 실제 제원·가용 명령을 측정.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "실제 재원을 알아야 적용 가능한거 아님? 먼저 서버 재원부터 확인하고 수정해야하지않음? … 해당 작업 가능한 프롬프트 작성해서 알려줘"
- 사용한 기법: (c) 재사용 산출물 — `agent/probe_server.sh`
- 결과: 읽기 전용·sudo 불필요 정찰 스크립트 작성(호스트/OS·Python·CPU/MEM·GPU(nvidia/rocm)·온도·디스크/NFS·스케줄러·mpirun·포털 접속성 8개 섹션). 맥에서 무에러 동작 확인. 각 서버 출력을 받아 `node_report.py`·`db.NODES`를 실제 제원에 맞게 조정 예정.
- 막힘 → 해결: 측정 없이 코드부터 맞추면 실서버에서 깨질 위험 → "측정 먼저, 적용 나중" 순서로 전환.

---

### [#15] 클러스터 루프 스캔 방식 + 실노드명(master·node1~13) 반영
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: 실제 HPC 구성(master + node1~node13)에 맞춰 노드 목록을 바꾸고, 노드마다 배포 대신 한 곳에서 SSH로 순회 스캔하는 방식으로 전환.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "HPC에서 노드가 master, node1, node2, ..., node13까지 있음 루프돌면서 정보 스캔하는 방식으로 수정"
- 사용한 기법: (b) SSH 순회 자동화, (c) 재사용 산출물(scan_cluster.sh)
- 결과: ① `db.NODES`를 `HPC_NODES` 환경변수로 주입 가능하게(기본 node01~08 유지 → mock·테스트 무손상). 실클러스터는 `HPC_NODES="master,node1,...,node13"`. ② `node_report.py`에 `--stdout` 추가. ③ **`agent/scan_cluster.sh`** 신설 — 한 호스트에서 master+node1~13을 SSH로 순회해 각 노드 `node_report.py --stdout` 결과를 `data/incoming/<node>.json`으로 수집(자기 자신은 로컬 실행). 포털이 다른 호스트면 `PORTAL_HOST` 설정 시 scp 전송. ④ README에 워크스테이션 직접 스캔(A)/master 경유 scp(B) 두 시나리오 정리. **검증**: HPC_NODES 주입 동작, pytest 5건 유지, 이 맥을 노드로 self-scan→ingest까지 로컬 실증.
- 막힘 → 해결: 노드명을 실제(master·node1~13)로 바꾸면 mock 샘플·테스트(node01~08)가 깨질 위험 → NODES를 env 주입형으로 만들어 실/데모 양립.

---

## 마무리 요약 (1~2줄)
- 가장 효과적이었던 에이전트 활용법: **인터뷰로 모호한 의도를 청사진 1문서로 수렴** → 그 문서에서 팀원별 핸드오버·킥오프 프롬프트를 파생해 충돌 0으로 병렬 착수.
- 다른 팀이 그대로 따라 하려면 필요한 것: `DEV_BLUEPRINT.md` 양식(역할·소유파일·DB·API·통합 접점·킥오프 프롬프트) + "공통 파일은 한 명만 수정" 규칙.
