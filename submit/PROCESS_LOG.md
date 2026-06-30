# PROCESS_LOG — 작업 기록 (과정 70점의 핵심 근거)

> 원칙: **실제로 시킨 프롬프트를 그대로 인용**할 것. 요약만 있으면 점수가 깎입니다.

## 작성자 정보 (개인별 로그 — 본인 것만)
- 팀명: team-d
- 본인 이름(작성자): 정승명 (jeongseungmyong)
- 공통과제(우리 팀이 자동화한 반복 수작업): HPC 사용자들이 **노드 사용 현황·서버 환경·노하우를 메신저/구두/개별 문의로 매번 확인·조율**하던 것 → 사내 HPC 통합 포털로 한곳에 모음.
- 내가 맡은 부분: **팀원2** — **사용량 통계(stats)** + **시스템 상태(system)** 페이지. 노드별 온도·디스크·NFS 점검과 노드별/사용자별 GPU 사용량 집계·추이. (SPEC §6 잠금 스키마 기준)
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

### [#6] 팀장 SPEC(잠금 6건) 반영 — 내 구현 정합 업데이트
- 작성자(팀원): 정승명 (팀원2)
- 목표: 팀장이 새로 올린 main의 `00_plan/SPEC.md`(잠금 6건)에 맞춰 내 두 페이지·라우터를 정합.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "새로 업로드된 main 브랜치를 업데이트하고 이것을 기반으로 팀원2(정승명)의 사용량 통계/시스템 상태 페이지 구현 업데이트"
- 사용한 기법: (b) git — origin/main(33643b0) 머지로 SPEC 반영 / (c) 재사용 산출물 — 기존 구현 위에 정합
- 결과:
  - **스키마 정합(SPEC §6 잠금)**: `node_health`를 `node/temp/disk_status/nfs_status/updated_at`로 축소(내가 확장했던 `gpu_temp`·`mem` 제거). `usage_log` NOT NULL 명시.
  - **데이터 포맷(SPEC §6.2)**: `sample_health.txt`를 헤더+위치기반 `NODE TEMP DISK_STATUS NFS_STATUS UPDATED_AT`로 교체, 상태값 소문자(`ok/warning/critical`·`ok/degraded/down`).
  - **API 키(SPEC §7.4)**: `GET /api/stats/usage` 응답 키를 `by_node`/`by_user`로 정정(확장 `summary`/`stacked`는 FR-S3로 유지). `GET /api/system/health`는 잠금 5필드만.
  - **잠금 반영**: 1A `get_db` 동시성표준(check_same_thread=False+WAL+busy_timeout, 통합 시 팀장 `db.py` 자동 사용) / 2A 멱등 초기화 / 5A 파서 입력 가드(헤더·빈줄·칸수·int try/except) / 6A **pytest 최소 세트** `tests/test_team2.py`(파서 정상·깨진행, 멱등 시드 2회, node01~08 정합, TestClient 200) — **4 passed**.
  - `system.html`: gpu/메모리 행 제거, 상태 칩 소문자 매핑, 추이 차트를 CPU 온도(평균·최고)로. 배너·필터 유지. `stats.html`: `by_node/by_user` 반영.
  - 검증: pytest 4건 통과 + Edge 헤드리스로 두 페이지 SPEC 정합 렌더 확인.
- 막힘 → 해결: ① 개인 로그가 main 머지로 팀장 항목과 섞임 → 내 항목만 남기고 정리. ② 스크래치 검증 하니스의 옛 `byNode` 진단 코드가 import 실패 유발 → 하니스를 순수 app 모듈로 교체.

---

### [#7] 공통 뼈대(hpc-portal)에 내 구현 이식 + .html 활성화
- 작성자(팀원): 정승명 (팀원2)
- 목표: 팀장이 올린 공통 뼈대(`hpc-portal/` 스캐폴딩)에 내 stats/system 구현을 이식하고 두 페이지를 실제 앱에서 활성화.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "새로 업로드된 main 브랜치를 업데이트하고 이것을 기반으로 팀원2(정승명)의 사용량 통계/시스템 상태 페이지 구현 업데이트하고 .html도 활성화 시작."
- 사용한 기법: (b) git — origin/main(afe6e56) 머지로 뼈대 반영 / (c) 재사용 산출물 — 내 리치 UI·차트 로직을 뼈대 규약에 맞춰 재사용
- 결과:
  - **라우터 보강**(`hpc-portal/routers/`): `system.py`에 `GET /api/system/history`(health_history 자기완결 확장, db.py 미수정) 추가, `stats.py` 응답에 `summary`·`stacked` 추가(핵심 키 `by_node/by_user/trend` 유지). 팀장 `db_dep` 의존성 패턴 그대로 사용.
  - **.html 활성화**(`hpc-portal/static/{system,stats}.html`): 스텁을 **공통 nav(`include.js` 자가주입)+`common.css` 토큰+Chart.js** 기반 리치 페이지로 교체 — 시스템: 위험 배너·전체/주의/위험 필터·CPU 온도 추이·노드 카드(게이지+디스크/NFS 칩). 통계: KPI 6종·추이·노드별·사용자순위·비중 도넛·노드별 사용자 구성(5차트). 채팅 위젯 한 줄 로드 유지.
  - **데이터/검증**: `data/sample_health.txt`를 collector 포맷 유지하며 데모 분포(정상4/주의2/위험2)로 정리. `tests/test_team2_ext.py` 추가(/history·summary·stacked) → **hpc-portal pytest 7 passed**(팀장 5 + 내 2). 실제 앱(`main.py`) 구동 → Edge 헤드리스로 두 페이지 공통 nav·차트·채팅 위젯 렌더 확인.
  - **정리**: 스캐폴딩 이전 위치였던 루트 `data/`·`routers/`·`static/`·`tests/` 중복 제거(단일 소스 = `hpc-portal/`).
- 막힘 → 해결: ① node_health가 이제 collector가 채우는 읽기 모델 → 내 라우터는 파싱 대신 읽기만, 온도 추이는 자기완결 확장 테이블로 분리(db.py 미수정). ② 개인 로그에 머지로 팀장 항목 유입 → 내 항목만 남김.

### [#8] 시스템 상태에 노드별 네트워크 상태 추가
- 작성자(팀원): 정승명 (팀원2)
- 목표: 시스템 상태 페이지의 CPU 온도 추이 그래프 아래에 노드별 네트워크 상태를 추가.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "시스템 상태에서 CPU 온도 추이 (평균 · 최고) 그래프 아래에 시스템 네트워크 상태를 추가 - 노드별 네트워크 상태"
- 사용한 기법: (c) 기존 노드 카드·게이지·색상 토큰 재사용
- 결과:
  - `hpc-portal/routers/system.py`: **node_net 자기완결 확장 테이블**(node·rx_mbps·tx_mbps·latency_ms·link_up·updated_at) + 멱등 시드 + **`GET /api/system/network`**(live 소폭 변동). SPEC 잠금 `node_health`·collector·`db.py`는 미수정.
  - `hpc-portal/static/system.html`: 온도 추이 아래에 **"시스템 네트워크 상태 (노드별)"** 섹션 — 노드 카드(상태 칩 정상/혼잡/포화/단절 + 1GbE 대역폭 사용률 바 + 수신/송신 Mbps + 지연 ms), 2.5초 폴링. 색상 판정은 사용률(70/90%)·지연(10/20ms)·링크 down 기준.
  - 검증: `GET /api/system/network` 200(8노드), pytest **7 passed**(네트워크 스키마 검증 추가), 실제 앱 구동 + Edge 스크린샷으로 섹션 렌더 확인(node02 포화·node05 혼잡·node06 단절).
- 막힘 → 해결: 네트워크는 SPEC 잠금 스키마에 없음 → collector/db.py 변경 없이 라우터 자기완결 확장 테이블로 추가(health_history와 동일 패턴).

### [#9] 사용량 통계 개편 — 추이 1주일 + 사용자별 용량 체크(기준 시점 버튼)
- 작성자(팀원): 정승명 (팀원2)
- 목표: 추이를 1주일 전부터 표시, 도넛·스택 차트를 제거하고 사용자별 용량 체크(기준 시점 전환) 추가.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "일자별 GPU 사용량 추이는 1주일 이전부터 표시. 사용자 사용량 비중, 노드별 사용자 구성은 없애고 사용자별 용량 체크 그래프 추가. 용량 체크는 매일 00시를 기본으로 보여주고 우측 상단에는 1주일전, 3일전, 현재시각을 체크할 수 있는 버튼을 만든다."
- 사용한 기법: (c) 기존 Chart.js·버튼 토글 패턴 재사용
- 결과:
  - `hpc-portal/routers/stats.py`: usage_log를 **최근 8일 범위에서 빈 날만 멱등 보충**(`_ensure_week_usage`, 날짜 기반 결정적 시드) → 추이가 1주일+ 표시. **`GET /api/stats/capacity`** 추가 — 사용자별 누적 GPU-hours를 기준 시점별(1주일전/3일전/오늘 00시/현재시각, `day<=cutoff`)로 반환. 미사용 `stacked` 응답 제거.
  - `hpc-portal/static/stats.html`: 추이 제목 "(최근 1주일)", **사용자 비중 도넛·노드별 사용자 구성 스택 제거**, **"사용자별 용량 체크"** 막대 차트 + 우상단 버튼 4종(기본 "오늘 00시" 활성, 클릭 시 client-side 전환) + 기준일 부제 추가.
  - 검증: 추이 8일(06-23~06-30) 응답 확인, `/api/stats/capacity` 4개 기준 시점 응답, pytest **7 passed**(추이≥7일·capacity 키·누적 단조 검증 추가), 실제 앱 스크린샷 확인.
- 막힘 → 해결: usage_log 기본 시드가 3일치뿐 → 내 소유 테이블이므로 빈 날만 멱등 보충해 추이·누적 용량 데이터 확보(db.py·collector 미수정).

### [#10] 사용량 통계 — '용량 체크'를 GPU-hours → 스토리지 용량(GB) 기준으로 변경
- 작성자(팀원): 정승명 (팀원2)
- 목표: 사용자별 "용량 체크"의 의미를 GPU-hours 누적이 아니라 **스토리지(디스크) 점유 용량(GB)**으로 바로잡기.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "사용량 통계에서 사용자별 용량 체크는 스토리지 용량입니다. 스토리지 용량 기준으로 변경."
- 사용한 기법: (c) 기존 기준시점 버튼·Chart.js 패턴 유지, 자기완결 확장 테이블 패턴 재사용
- 결과:
  - `hpc-portal/routers/stats.py`: GPU-hours 누적합 로직 제거 → **자기완결 `user_storage(user,day,used_gb)` 테이블**(날짜·사용자 결정적 시드, 과거→현재 단조 증가) + **`GET /api/stats/capacity`가 기준 시점별 스토리지 GB '스냅샷'** 반환(누적합 아님). `used_gb` 키로 교체.
  - `hpc-portal/static/stats.html`: 제목 "사용자별 용량 체크"→**"사용자별 스토리지 용량"**, 차트 단위/툴팁 "스토리지(GB)", 부제 "사용자별 스토리지 점유 용량(GB)", 데이터 매핑 `used_gb`로 변경.
  - 검증: `/api/stats/capacity` 기준시점 총량 단조 증가(2903→3025→3098→3116 GB), 사용자별 현실적 GB(park≈1.2TB·kim≈850GB), pytest **7 passed**(capacity 스키마 `used_gb`·증가 검증으로 갱신).
- 막힘 → 해결: 스토리지는 GPU-hours와 무관한 '점유 용량'(시점 스냅샷) → usage_log를 건드리지 않고 db.py 미수정 자기완결 `user_storage`로 분리(온도·네트워크와 같은 '운영 가시성' 확장 패턴).

### [#11] 서버용량(디스크) 체크 — 빠른 스냅샷 + 직관적 게이지 시각화 (시스템 상태 & 사용량 통계)
- 작성자(팀원): 정승명 (팀원2)
- 목표: 서버 용량 체크 시 전 파일을 du 로 스캔하면 오래 걸림 → 미리 적재한 스냅샷으로 빠르게 보고, 시각화를 직관적으로.
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "서버용량 체크 부분에서 모든 파일을 찾고 체크할 때 시간이 많이 소요되어 빠르게 체크한 후 시각화도 직관적으로 수정."
- 사용한 기법: (c) 기존 노드 카드·게이지(.bar/.fill)·임계 색상 토큰 재사용, 자기완결 확장 테이블 패턴
- 결과:
  - `hpc-portal/routers/system.py`: 자기완결 **`node_disk(node, used_gb, total_gb, updated_at)`** 멱등 시드 + **`GET /api/system/disk`**(used_pct 계산, live 소폭 변동). 전 파일 스캔 없이 **스냅샷 즉시 응답 = 빠른 체크**. health disk_status(node03 warn·node06 crit)와 정합.
  - `hpc-portal/static/system.html`: "서버 디스크 용량(노드별)" 섹션 — **사용률 게이지 바 + 사용/전체/여유 GB**, 임계 색상(70/90%), **클러스터 전체 요약(사용/총·%)**, 2.5초 폴링.
  - `hpc-portal/routers/stats.py`: `GET /api/stats/capacity` 응답에 **쿼터(quota_gb)·사용률(used_pct)** 추가, 사용률 내림차순 정렬.
  - `hpc-portal/static/stats.html`: 사용자별 스토리지를 막대차트→**쿼터 대비 직관적 게이지 행**(used/quota GB·% + 색)으로 개선.
  - 검증: `/api/system/disk` 8노드(node06 96.2%·node02/03 75~78%), `/api/stats/capacity` 사용률 정렬·정합, pytest **7 passed**(disk 스키마·used_pct·정렬 검증 추가).
- 막힘 → 해결: 디스크 정량 용량은 SPEC 잠금 node_health/sample_health 스키마에 없음 → collector/db.py 변경 없이 자기완결 node_disk 로 추가(network·history와 동일 패턴).

### [#12] 시스템 상태 — 서버 디스크 용량(노드별) 섹션 제거
- 작성자(팀원): 정승명 (팀원2)
- 목표: 시스템 상태 페이지에서 서버 디스크 용량(노드별) 섹션을 삭제(요구사항 변경).
- 에이전트에게 시킨 것(실제 프롬프트 핵심 인용):
  > "시스템 상태에서 서버 디스크 용량(노드별)은 삭제."
- 사용한 기법: 기능 제거(프론트 섹션 + 백엔드 엔드포인트/테이블/테스트 일괄 정리)
- 결과:
  - `hpc-portal/static/system.html`: "서버 디스크 용량(노드별)" 섹션·게이지 카드·`loadDisk`/`diskCard`/폴링 제거.
  - `hpc-portal/routers/system.py`: `node_disk` 자기완결 테이블·시드·**`GET /api/system/disk`** 제거, docstring 정리. (온도추이·네트워크 확장은 유지)
  - `hpc-portal/tests/test_team2_ext.py`: `/api/system/disk` 검증 제거. pytest **7 passed**.
  - 사용량 통계의 '사용자별 스토리지 용량'(별도 `user_storage`)·system의 `disk_status`(health)는 그대로 유지.
- 막힘 → 해결: 없음(자기완결 확장이라 health·db.py 영향 없이 깔끔 제거).

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

## 마무리 요약 (1~2줄)
- 가장 효과적이었던 에이전트 활용법: **계획 선확정 → 단독 구현 → 팀 SPEC(잠금) 정합 → 공통 뼈대 이식·활성화**까지, 소유 경계 안에서 충돌 없이 통합(pytest 7건 + 헤드리스 스크린샷으로 실앱 검증).
- 다른 팀원이 그대로 따라 하려면 필요한 것: 뼈대 규약(`db_dep` 읽기 모델 + `common.css`/`include.js` nav + collector가 채우는 node_health) 위에 자기 라우터·페이지만 얹기. 확장 기능은 db.py 미수정 자기완결 테이블로.
