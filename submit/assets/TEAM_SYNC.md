# TEAM_SYNC — 팀원 필수 검토 (2026-06-30 실서버 반영본)

> **이 문서를 먼저 읽어라.** 뼈대·모니터링·실서버 데이터 연동이 끝난 뒤의 **현재 상태**와, 너희가 **반드시 검토해야 할 변경 3가지**를 담았다.
> 자기 파트 상세는 `submit/assets/handover/member1_wiki_chat.md`(팀원1) · `member2_stats_system.md`(팀원2). 확정 스펙은 `00_plan/DEV_BLUEPRINT.md`. 충돌 시 **이 문서 > 핸드오버 문서**(핸드오버는 실서버 전 작성분).

---

## 0. TL;DR (3줄)
1. 공통 뼈대 + 라우터 5개 등록 + 모니터링 + **실서버 데이터 파이프라인까지 배선 완료**. 너희는 **자기 HTML에 fetch만** 채우면 `git pull`로 합쳐진다(소유 파일이 갈려 충돌 0).
2. **너희 라우터(stats/system/wiki/chat)는 이미 동작한다.** `/docs`에서 바로 응답 확인 가능 — 새로 만들 게 아니라 화면(fetch+렌더)만 채우면 된다.
3. **딱 3가지가 바뀌었으니 필수 검토** → §2. ① 노드명 하드코딩 금지(동적 렌더) ② GPU 없음(CPU·예보모델 중심) ③ 실행 모드 2개(mock 개발 / ingest 실데모).

---

## 1. 지금 상태 (무엇이 끝났나)
- `hpc-portal/` FastAPI+SQLite 앱 가동. `main.py`에 **라우터 5개(monitoring/wiki/chat/stats/system) 등록 완료** — 팀장에게 따로 요청할 것 없음.
- **모니터링 페이지 완성**: 실클러스터(master+node1~13)에서 CPU·MEM·실행 중 예보모델(pschism/padcirc/nemo/swan)을 라이브로 표시. → **레퍼런스 구현으로 그대로 베껴 써라**(`hpc-portal/static/monitoring.html`: 동적 노드 렌더 + 3초 폴링 + fetch 패턴).
- **데이터 수집 파이프라인 완성**: master에서 `agent/scan_once.sh` 1회 실행 → `data/incoming/*.json` → 포털 `COLLECTOR=ingest` 가 읽어 `nodes/jobs/node_health` 채움. (팀장이 운영)

## 1.1 너희가 채울 것 (요약)
| 팀원 | HTML(채울 것) | 라우터(이미 동작) | 비고 |
|---|---|---|---|
| 팀원1 | `static/wiki.html`, `static/chat-widget.js` | `GET /api/wiki/servers`·`/posts`, `POST /api/wiki/posts`, `GET/POST /api/chat/messages` | 채팅 위젯은 신규 제작(자체 주입) |
| 팀원2 | `static/stats.html`, `static/system.html` | `GET /api/stats/usage`, `GET /api/system/health` | 차트 Chart.js 4.4.1 CDN |

> `wiki.html`·`stats.html`·`system.html` 은 현재 **헤더-only 스텁**(TODO 주석 있음). 채팅 위젯 한 줄은 이미 들어가 있다.

---

## 2. 필수 검토 — 실서버로 바뀐 3가지 (★ 반드시)

### ① 노드명은 하드코딩 금지 — API 응답대로 동적 렌더 (가장 중요)
원래 핸드오버는 "노드는 무조건 `node01~node08`"이라고 했지만 **실클러스터는 `master, node1 … node13`**(zero-pad 없음, 총 14대)다. 모드에 따라 노드 집합이 다르다:
- 개발(mock 기본): `node01 … node08`
- 실데모(ingest): `master, node1 … node13`

→ **드롭다운·카드·표·차트 라벨을 API 응답에서 동적으로 생성**하라. 노드 개수·표기를 코드에 박지 마라. (모니터링이 이렇게 동작한다 — `monitoring.html` 의 `fillNodeSelect()` / `nodesData.map(...)` 참고.) 이렇게만 하면 mock·실데모 양쪽에서 코드 변경 없이 돈다.

### ② GPU 없음 — CPU·예보모델 중심
실측: AMD EPYC CPU 클러스터, **GPU 0개**. 실제 작업은 `pschism / padcirc / nemo / swan / Intel-MPI`(해양·폭풍해일·파랑 예보 모델).
- **팀원2 stats**: "GPU 점유/사용률" 표현을 쓰지 마라. `usage_log` 의 컬럼명은 `gpu_hours`지만 **레거시 이름일 뿐 의미는 '사용(코어·작업)시간'** → UI 라벨은 `사용시간`/`코어시간`으로. 막대·추이 차트 구조는 그대로 OK.
- **팀원2 system**: `temp/disk/nfs` 그대로 유효. (실데이터 현재 `temp=0` 은 팀장이 sensors 보정 예정 — 너는 받은 값 그대로 렌더만 하면 됨.)
- **팀원1 wiki**: 서버 환경 카드의 예시 스펙을 CPU 클러스터에 맞춰도 좋다(필수는 아님). `servers` 시드는 이미 들어가 있다.

### ③ 실행 모드 2개 — 너는 mock으로 개발
- **개발(기본)**: 그냥 `uvicorn main:app --reload` → `COLLECTOR=mock`, 노드 `node01~08`. 너의 작업은 전부 이 모드로 충분.
- **실데모**: 팀장이 `COLLECTOR=ingest` + `HPC_NODES=master,node1,…,node13` 로 띄우고 master에서 `scan_once.sh` 로 수집. 너는 신경 쓸 것 없고, **①(동적 렌더)만 지키면** 실데모에서도 그대로 보인다.
- 참고: `usage_log`(stats)는 컬렉터가 안 채우는 **독립 시드**(현재 node01~08, 누적/추이용)다. 실노드명과 맞추고 싶으면 시드를 `master,node1~13`로 바꾸면 되지만 필수는 아니다.

---

## 3. 변치 않는 통합 규칙 (그대로 유효)
- **자기 소유 파일만 수정.** 공통(`main.py`/`db.py`/`common.css`/`_nav.html`/`include.js`/`index.html`)은 팀장만. 라우터 등록은 이미 끝났으니 요청 불필요.
- **채팅 위젯**: `monitoring/wiki/stats/system` 4페이지에 `<script src="/static/chat-widget.js"></script>` **한 줄**(팀원1 제작, 자체 CSS·폴링 주입). **`index` 제외.** stats/system엔 이미 한 줄 들어가 있다.
- **디자인 토큰**(DEV_BLUEPRINT §5): `<html lang="ko">`, CSS 변수(`--bg/--paper/--ink/--blue/--green/--orange/--red` 등), 네비 네이비 + `.active`. 색 임계: 정상 green / 주의 orange / 위험 red.
- **시간 표기**: 화면 `"HH:MM"`, 저장 ISO 문자열.
- **각 API는 `/docs`에서 단독 200 응답**(통합 전제). 이미 충족되어 있으니 깨지 마라.

---

## 4. 참고 자료 (읽는 순서)
1. **이 문서(TEAM_SYNC.md)** — 현재 상태 + 필수 검토.
2. `submit/assets/handover/member{1,2}_*.md` — 자기 파트 상세(소유 파일·API·완료 기준·킥오프 프롬프트). 단, 노드명/GPU 부분은 §2가 우선.
3. `00_plan/DEV_BLUEPRINT.md` — 확정 스펙(§4 DB, §5 토큰, §6 API).
4. `hpc-portal/CLAUDE.md` — 앱 기술 가이드(컬렉터 seam·계약·실행).
5. `hpc-portal/static/monitoring.html` — **레퍼런스 구현**(동적 렌더·폴링·fetch). 새 페이지는 이걸 본떠라.

---

## 5. 합치는 절차 + 통합 체크리스트
**절차**
1. 팀원: 자기 파일만 커밋·푸시 (`git add static/... routers/...; git commit; git push`).
2. 팀장: `git pull` → 소유 파일이 달라 **자동 머지**.
3. 실데모: `HPC_NODES=master,node1,…,node13 COLLECTOR=ingest uvicorn main:app` + master `scan_once.sh` → 5페이지 스모크.

**통합 시 팀장이 점검(필수 검토 항목)**
- [ ] 노드명 하드코딩 없음 — mock(node01~08)·실데모(master,node1~13) **양쪽에서 페이지 정상**
- [ ] GPU 표현 제거(stats는 사용/코어시간으로)
- [ ] 채팅 위젯이 `wiki/stats/system` 에서 뜸(`index` 제외)
- [ ] `/docs` 에서 5개 라우터 단독 응답
- [ ] 디자인 토큰·`"HH:MM"` 표기 일치
- [ ] `git pull` 충돌 0 (자기 소유 파일만 건드렸는지)
