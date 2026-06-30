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

---

## 마무리 요약 (1~2줄)
- 가장 효과적이었던 에이전트 활용법: **계획 선확정 → 단독 구현 → 팀 SPEC(잠금) 정합 → 공통 뼈대 이식·활성화**까지, 소유 경계 안에서 충돌 없이 통합(pytest 7건 + 헤드리스 스크린샷으로 실앱 검증).
- 다른 팀원이 그대로 따라 하려면 필요한 것: 뼈대 규약(`db_dep` 읽기 모델 + `common.css`/`include.js` nav + collector가 채우는 node_health) 위에 자기 라우터·페이지만 얹기. 확장 기능은 db.py 미수정 자기완결 테이블로.
