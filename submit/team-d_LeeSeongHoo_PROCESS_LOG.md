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

### [#16] 정찰 결과 반영 + 망격리 확인 + 사무실 PC 핸드오버 준비
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: 실측으로 드러난 제약(python3 없음·GPU 없음·PBS·망격리)에 맞춰 수집기를 만들고, 망이 안 닿는 이 맥에서 사무실 PC로 작업을 통째로 넘길 준비.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "서버의 master에서 외부 통신이 가능할탠데? 우리쪽에서 막혀있는거 아님?"
  > "저 서버 조회가 가능한 워크스테이션에서 정보 가져오고 이쪽으로 쏘려고 함 이거 테스트 가능?"
  > "ignore 무시하고 로그까지 전부 내용에 포함되도록 이동 준비"
- 사용한 기법: (b) 망 진단(ip route/nc), (c) 재사용 산출물(collect_node.py·HANDOFF.md)
- 결과: 정찰 14노드 실측 → master+node1~13/RHEL7.9/**python3 없음**/**GPU 없음**/PBS/실작업 pschism·padcirc·nemo·swan. 망 진단: 맥↔클러스터 양방향 직접통신 불가(게이트웨이 방화벽 timeout), git만 연결. `collect_node.py`(py2.7 호환, CPU/MEM+ps 상위작업) 작성·JSON 검증. git경유 전송 `scan_push.sh`. **핸드오버**: `HANDOFF.md` 작성(상태·실측·망구조·다음할일 — 최우선 UI를 GPU→CPU reframe), `submit/` 전체를 `git add -f`로 강제 추가(로그·증빙·자산 git에 포함)해 사무실 PC가 clone만으로 이어받게 함.
- 막힘 → 해결: master가 GitHub엔 나가지만 맥(사설IP)엔 못 닿음(외부=인터넷 ≠ 타 사설대역) → git 전송으로 우회. 직접연동(실시간)은 클러스터에 닿는 사무실 PC에서 이어가기로.

---

### [#17] 사무실 PC에서 실서버 직접 연동 — collect_node.py 실노드 첫 실행 검증
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: 클러스터에 닿는 사무실 PC(10.27.1.103)에서 master로 직접 SSH해, py2.7 수집기 `collect_node.py`가 실노드에서 처음 도는지 검증(망격리 git릴레이 우회 → 직접 ssh/scp).
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "지금까지 내용 검토 후 핸드오프 내용 검토하고 이어서 진행 가능함? 다만, 여기서는 서버와 직접 통신이 가능하니 서버 정보는 내가 알려줄것임."
  > "마스터에서 노드들 접근 가능함. 다만 원격서버 마스터에서만 각 노드들 정보 수집하고, 마스터랑 여기랑만 통신"
  > "추가로 원격서버 부하가 최소한으로 걸리도록 주의해서 작업할것."
- 사용한 기법: (b) 외부 서버 직접 연동(SSH/scp), (c) 재사용 산출물(collect_node.py)
- 결과: 이 PC `~/.ssh/config`의 `Geo83-gonas`(27.112.246.62:50023, user gonas, id_rsa 키인증)로 master 접속 확인. master repo가 2커밋 뒤처져(`collect_node.py` 없음) → `git pull --ff-only`로 `9530e47` 최신화(NFS 공유홈이라 전 노드 즉시 반영). master 로컬 실행 OK(실작업 schism 스크립트 포착), **node1 검증 OK**(cpu 96%·mem 23%, 실작업 `pschism`/user gonas 3건 JSON). 부하 최소화: --loop 없이 1회성·짧은 ConnectTimeout·읽기전용만.
- 막힘 → 해결: 토폴로지가 이 PC↔master만(노드는 master 경유) → 노드 수집은 master에서 ssh 순회로 수행키로. 두 노드 모두 `temp:0`(EPYC sensors 포맷이 온도 정규식과 불일치) → CPU 클러스터라 비치명, 보정 후보로 기록.

---

### [#18] 실서버 → 포털 엔드투엔드 가동 — 라이브 14노드 수집·표시 검증
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: master 1회성 순회 수집 → 이 PC scp → 포털 `COLLECTOR=ingest` 적재 → API 응답까지 전 구간을 실데이터로 가동·검증(망격리 git릴레이 없이 직접연동).
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "계속 진행"
  > (토폴로지) "원격서버 마스터에서만 각 노드들 정보 수집하고, 마스터랑 여기랑만 통신"
  > "원격서버 부하가 최소한으로 걸리도록 주의해서 작업할것."
- 사용한 기법: (b) 외부 서버 직접 연동(SSH 순회 + scp), (c) 재사용 산출물(scan_once.sh·ingest 컬렉터)
- 결과: `scan_once.sh` master 1회 실행 → **14/14 성공**(master+node1~13) → `data/incoming/*.json` 14개를 이 PC로 scp. 포털을 in-process(TestClient, COLLECTOR=ingest, HPC_NODES=master,node1~13, 임시DB)로 가동 → lifespan startup이 ingest로 nodes=14·jobs=30·health=14 적재, `/api/monitoring/nodes`·`/jobs`·`/api/system/health` 200 OK. **라이브 결과**: node1·2·3 pschism(gonas), node5·7·8 padcirc(smjeong), node9 nemo(gonas), node10 Intel-MPI(hcpark), node11 swan(hcpark), node4·6·12·13 idle. "누가·어느 노드·무슨 예보모델"이 그대로 노출 — 포털 핵심가치 실증.
- 막힘 → 해결: ① venv에 fastapi 미설치 → `pip install -r requirements.txt`(fastapi 0.138.2). ② 노드명이 master/node1~13이라 기본 db.NODES(node01~08)면 ingest가 전부 reject → `HPC_NODES` 주입으로 수용. ③ 잔여 이슈: 전 노드 temp=0(EPYC sensors 포맷 불일치), MPI 작업이 노드당 3행(상위 CPU 3개)으로 중복 표시 → 모니터링 UI reframe에서 집계·정리 예정.

---

### [#19] 모니터링 UI를 CPU 중심으로 reframe — 실데이터 렌더 검증
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: GPU 전제(평균 GPU KPI·GPU 막대·GPU 사용률 차트·node01~08 고정 드롭다운)였던 모니터링 페이지를 실측 제약(GPU 없음·CPU 클러스터·실작업이 예보모델)에 맞게 CPU 중심으로 전환. "누가·어느 노드·무슨 모델"을 주인공으로.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "계속 진행" (핸드오프 우선순위 #2: 모니터링 UI를 CPU 중심으로 reframe — GPU 막대/차트 → CPU%·MEM·현재 모델작업(사용자), Job 테이블이 주인공)
- 사용한 기법: (b) 외부 도구(browse.exe 헤드리스 렌더 검증), 실데이터 연동
- 결과: `static/monitoring.html` 전면 개편 — ① GPU 전부 제거(KPI '평균 CPU/MEM', GPU 막대/태그 삭제, 차트 '노드별 CPU 사용률'). ② 노드 카드에 실행 중 예보모델 표시(`jobs` 를 노드+모델명으로 집계, MPI 랭크 N개 → '×N proc'). ③ Job 테이블 재구성(노드/사용자/모델·명령/프로세스수/상태), pschism·padcirc·nemo·swan 모델명 친화 추출. ④ 등록폼 노드 드롭다운을 실데이터(master,node1~13)로 동적 생성. **검증**: uvicorn(ingest) 구동 → browse.exe 렌더 → 노드카드 14·Job행 10(30 raw 집계)·평균CPU 79%·페이지 내 'GPU' 문자열 0건, 스크린샷 확인.
- 막힘 → 해결: collect_node.py가 상위 CPU 프로세스를 잡다 보니 node10은 실제 모델 대신 Intel-MPI 런처(hydra_pmi_proxy)가 표시됨 → 비치명(런처도 누가·어디서는 정확). 모델명 정밀화는 후속 후보.

---

### [#20] 팀원 배포용 통합 가이드(TEAM_SYNC) — 실서버 반영 필수 검토 정리
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: 실서버 연동·모니터링 reframe 이후 바뀐 전제를 팀원이 참고/필수검토할 형태로 메인 브랜치에 담아 배포. 기존 핸드오버(실서버 전 작성)의 어긋난 부분 정정.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "각자 팀원들이 참고해야하는, 그리고 필수로 검토해야하는 사항 반영해서 메인 브랜치에 담아주고 팀원에게 배포할것임"
- 사용한 기법: (c) 재사용 산출물(팀원 배포 문서), 실코드 대조(라우터 스텁 동작 확인)
- 결과: 루트 `TEAM_SYNC.md` 신규 — ①현재상태(뼈대·라우터5·모니터링·수집 파이프라인 완료, 팀원은 HTML fetch만) ②필수검토 3가지(노드명 하드코딩 금지·동적 렌더 / GPU 없음=CPU·예보모델 / 실행모드 mock·ingest) ③불변 통합규칙 ④참고자료 순서 ⑤합치는 절차+체크리스트. 확인: stats/system 라우터는 이미 DB 집계 반환(동작 스텁) → 팀원은 화면만. 기존 핸드오버 3종(README·member1·member2) 상단에 "TEAM_SYNC 우선" 배너 + member2의 어긋난 2줄(GPU 점유→사용/코어시간, node01~08 고정→API 동적 렌더) 정정.
- 막힘 → 해결: 핸드오버가 node01~08 고정·GPU 전제라 그대로 두면 팀원이 실데모에서 깨짐 → 단일 진실 공급원을 TEAM_SYNC로 올리고 기존 문서엔 우선순위 배너로 연결(문서 전면 재작성 대신 최소 정정).

---

### [#21] 팀원 브랜치 통합 — 완성본 빌드(5페이지+채팅) + 사이드바 전역 통일
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: 팀원 작업이 올라온 개인 브랜치(kimminju·jeongseungmyong)를 받아 충돌 없이 합쳐 동작하는 완성본을 만들고, 네비 디자인 충돌을 해소.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "팀원들의 작업도 완료되서 각 팀원 이름의 브랜치로 올라왔음 이거 풀해서 완성본 만들것"
  > (네비 통일 결정) "사이드바로 전역 통일 (추천)"
- 사용한 기법: (a) 역할분담 결과 병합, (b) git 브랜치 통합 + browse.exe 렌더 검증
- 결과: 경계 점검 — **코드는 소유분리로 충돌 0**(kim=wiki/chat+위젯, jeong=stats/system+health). 단 ① kim이 공통 `_nav.html`을 좌측 사이드바로 재디자인(theme.css) + include.js 모바일토글 추가 ② 두 팀원이 공유 `PROCESS_LOG.md`에 각자 로그를 덮어씀. 처리: 사이드바 디자인을 팀 표준으로 채택 → 나머지 4페이지(monitoring/stats/system/index)에 `theme.css` 한 줄 추가, 사이드바 라벨 GPU→CPU 정정. 개인 로그는 **이름별 파일로 분리**(`team-d_kimminju_…`·`team-d_jeongseungmyong_…` 생성, 내 `team-d_LeeSeongHoo_…`·공유 PROCESS_LOG는 보존). **검증**: pytest 13건 통과(팀원 테스트 포함), 5페이지 전부 좌측 고정 사이드바로 렌더(browse.exe 스크린샷), `/api/wiki/posts`·`/monitoring/nodes`·`/system/health`·`/stats/usage` 200. 실데모(ingest) 기준 monitoring 14노드 라이브.
- 막힘 → 해결: ① 사이드바는 theme.css 필요한데 4페이지가 common.css만 → theme.css 링크 주입으로 전역 통일. ② 팀원 PROCESS_LOG 덮어쓰기 → 이름별 분리로 3인 로그 모두 보존(전원참여 증빙). 잔여(비치명): system의 'node01~08' 헤더 텍스트·mock 네트워크 패널, stats 노드명 혼재 → 팀원 자료 다듬기 후속.

---

### [#22] 통합 후 다듬기 — 노드명 전 페이지 일관(실노드 기준)
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: 통합본에서 실데이터(master,node1~13)와 표기가 어긋나던 잔여 부분(stats 노드명 혼재, system 목업 네트워크 패널·헤더 텍스트)을 실노드 기준으로 정리.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "남은 다듬기 해줘"
- 사용한 기법: (b) browse.exe 렌더 재검증, 실데이터 대조
- 결과: ① `db.py` usage_log 기본시드를 `node01~08` 하드코딩 → `db.NODES` 매핑(`nd(i)=NODES[i%len]`)으로 변경 → mock/실모드 모두 노드명 일치(stats 사용노드 16→11, node01~08 잔재 제거). ② `system.py` 네트워크 시드 `_NET_SEED`(node01~08 고정) → `_net_for(node,idx)` 결정적 생성 + `NODES` 순회로 동적화(실노드명, 일부 노드 포화/단절 유지). docstring '(node01..08)'→'(db.NODES 기준)'. ③ `system.html` 문구 'node01~08 …'·'노드별 상태 (node01~08)' → 일반화. **검증**: pytest 13 통과, ingest 재구동 후 system 네트워크·노드카드·stats 노드차트 전부 master,node1~13으로 일관(스크린샷), 'node01' 페이지 내 0건.
- 막힘 → 해결: stats 추이 차트가 headless 캡처에서 가끔 늦게 그려짐 → 차트 인스턴스 점검 시 데이터·라벨 정상, resize 시 정상 페인트 확인 → 실브라우저 ResizeObserver로 정상(코드 결함 아님)으로 판단.

---

### [#23] 노드 온도 수집 — 실측 + 센서 없는 노드 추정 fallback (전 노드 가시화)
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: 전 노드 temp=0(시스템 페이지 온도 0℃·추이 평탄)을 해결. 실측 시도 후 안 되는 노드는 더미로라도 가시화.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "온도 잡기 시도해보고 안되면 목업 더미로 만들어서 가시화만 해도 좋음."
- 사용한 기법: (b) 실서버 직접 진단(node1 `sensors` 실측), 수집기 보정
- 결과: node1 `sensors` 실측 → **CPU 코어 온도 센서(k10temp/Tctl) 미노출**, NIC 어댑터 온도 `loc1 +45.0℃`만 존재. `collect_node.py` `temp_c()`를 "CPU 계열(Tctl/Tdie/Tccd/Package/Core) 우선 → 없으면 임계값(high/crit) 제외한 실센서 최댓값"으로 개선 → 10/14 노드가 실측(43~52℃). 센서가 아예 없는 4노드(node6·12·13 등)는 `main()`에서 CPU 부하 기반 추정치(유휴38℃~만부하58℃)로 채워 0 제거. 배포→master 재스캔→scp 반영. **검증**: /api/system/health 14노드 38~52℃(0 없음), /history 31포인트(평균~44·최고56), 시스템 페이지 최고온도 52℃·온도추이 파형·노드카드 온도 전부 표시(스크린샷).
- 막힘 → 해결: EPYC에서 CPU 코어 온도가 lm_sensors에 안 올라옴 → NIC(loc1) 실온도를 대체 사용(0 더미보다 정확), 그조차 없는 노드만 부하기반 추정. 실측/추정 혼재이나 가시화·시연 목적엔 충분(사용자 승인).

---

### [#24] 외부 LAN 공개 서버 + 저빈도 자동갱신 + 홈 KPI GPU→CPU
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: 완성본을 사무실 LAN에 공개(외부 PC 접속)하고, 라이브 갱신을 저빈도로 돌리고, 홈 화면의 GPU 표시(항상 0)를 CPU로 교체.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "서버 올려주고 외부에서 접근 가능하게 웹서버 열여줘"
  > "서버에서 저빈도 갱신 걸어주고, 메인 인덱스 페이지에서 지피유 사용량이라 0으로만 나옴 시피유로 바꿔줄것"
- 사용한 기법: (b) 외부 서버 직접 연동, 분리(detached) 프로세스 운영
- 결과: ① 서버를 `0.0.0.0:8000`(ingest 실데이터)로 공개. 단 run_in_background는 ~2분 타임아웃에 죽어 **`Start-Process` 분리 프로세스**로 전환(생존 확인). 관리자 권한 부재로 방화벽은 사용자에게 1줄(`New-NetFirewallRule … -LocalPort 8000 -RemoteAddress 10.27.1.0/24`) 안내. 재시작용 `run_server.bat` 추가. URL http://10.27.1.103:8000. ② **저빈도 자동갱신** `refresh_loop.ps1`(이 PC→master `scan_once` + scp, 기본 180초, 읽기전용·병렬없음) 분리 실행 + `run_refresh.bat`. 포털은 5초마다 incoming 재적재 → 화면 자동 반영. 첫 사이클 'refreshed (14 nodes)' 확인. ③ `static/index.html` '평균 GPU 사용률'(n.gpu, 항상 0) → '평균 CPU 사용률'(n.cpu) + 카드 설명 GPU 문구 제거. 검증: 홈 KPI '평균 CPU 사용률 67%', 페이지 내 GPU 0건.
- 막힘 → 해결: ① 백그라운드 서버가 2분 타임아웃에 종료 → Start-Process 분리 + 사용자용 .bat로 내구성 확보. ② Public 프로필·비관리자라 방화벽 자동개방 불가 → 관리자 1줄 안내(대역 10.27.1.0/24 한정).

---

### [#25] 제출물 최종 정리 — 산출물·Before/After·개인로그·재사용자산
- 작성자(팀원): LeeSeongHoo (팀장)
- 목표: 제출 4종(산출물·효과측정·개인 PROCESS_LOG·재사용 자산)을 submit/ 기준으로 완성·점검.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "지금까지 내용 완전히 정리하고, 제출해야하는 결과물 정리할것. 산출물, 비포_에프터, 내 프로세스 로그, 재사용자산(에셋)"
- 사용한 기법: (c) 재사용 산출물 정리
- 결과: ① **재사용 자산 보강** — `assets/QUICKSTART.md`(10분 실행: mock·실연동·외부공개·구조), `assets/prompts.md`(단계별 실제 프롬프트), `assets/CLAUDE_hpc-portal.md`·`assets/TEAM_SYNC.md` 사본, `assets/README.md` 전체 인덱스(컬렉터 seam·agent 수집기·운영 스크립트 포인터 포함). ② **CHECKLIST.md** 전 항목 ✅ + 위치 명기(발표자료만 팀 작성 잔여). ③ **BEFORE_AFTER.md** '최종 달성(라이브 데모)' 추가(실데이터 14노드·온도·표기일관·외부공개·pytest13). ④ **개인 로그** `team-d_LeeSeongHoo_PROCESS_LOG.md`(#1~#25) 동기화, 팀 3인 로그 포함. ⑤ 산출물=`hpc-portal/`(5페이지+채팅+실서버 ingest).
- 막힘 → 해결: 없음(정리 작업). 제출은 프로젝트 폴더 전체 zip — 개인 로그는 영문 파일명으로 충돌 없이 모임.

---

## 마무리 요약 (1~2줄)
- 가장 효과적이었던 에이전트 활용법: **인터뷰로 모호한 의도를 청사진 1문서로 수렴** → 그 문서에서 팀원별 핸드오버·킥오프 프롬프트를 파생해 충돌 0으로 병렬 착수.
- 다른 팀이 그대로 따라 하려면 필요한 것: `DEV_BLUEPRINT.md` 양식(역할·소유파일·DB·API·통합 접점·킥오프 프롬프트) + "공통 파일은 한 명만 수정" 규칙.
