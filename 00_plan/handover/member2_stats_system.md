# 팀원2 핸드오버 — 사용량 통계 + 시스템 상태

> **받는 법**: 팀 git 저장소를 `git clone`(또는 `git pull`) → **네 세션**에서 이 문서 + `00_plan/DEV_BLUEPRINT.md`를 첨부/붙여넣고 시작. 공통 규칙(디자인 토큰·노드 명명 등)은 DEV_BLUEPRINT가 단일 진실 공급원이다.

---

## 0. 네가 만들 것 (한 줄)
노드별/사용자별 **사용량 통계**(집계·추이 차트) 페이지와, 온도·디스크·NFS 등 **시스템 상태** 점검 페이지. + 추가 아이디어 캐치올.

## 1. 소유 파일 (★ 이것만 수정 — 공통 파일은 팀장 경유)
```
routers/stats.py         # /api/stats/*
routers/system.py        # /api/system/*
static/stats.html        # 사용량 통계 화면
static/system.html       # 시스템 상태 화면
data/sample_health.txt   # 온도/디스크/NFS 목업 (네가 작성)
```
> `main.py`·`db.py`·`common.css`·`_nav.html`은 **건드리지 말 것.** 라우터 2개 등록은 팀장이 `main.py`에 한 줄씩 해준다.

## 2. DB 테이블 (네 소유)
```sql
node_health(node PK, temp, disk_status, nfs_status, updated_at)   -- node01~08
usage_log(id PK, node, user, gpu_hours, day)                      -- 집계 시드(자체 보유 → 독립)
```
- `node_health`는 `sample_health.txt`를 파싱해 시작 시 적재.
- `usage_log`는 통계용 시드 데이터를 직접 채운다(독립성 위해 팀장 테이블에 의존하지 않음). 더 풍부하게 하려면 `/api/monitoring/jobs`를 **GET으로만** 읽어 보강(쓰기 금지).

### `sample_health.txt` 권장 형식 (파싱 쉬운 한 줄 = 한 노드)
```
node01 temp=42 disk=OK   nfs=OK
node02 temp=51 disk=OK   nfs=DEGRADED
node03 temp=68 disk=WARN nfs=OK
...
node08 temp=39 disk=OK   nfs=OK
```

## 3. API 엔드포인트 (네 소유)
```
GET  /api/stats/usage     사용량 집계 (노드별/사용자별/추이). 예: {byNode:[...], byUser:[...], trend:[...]}
GET  /api/system/health   노드별 온도·디스크·NFS 상태 목록
```
- 각 API는 **다른 사람 코드 없이 `/docs`에서 단독 응답**해야 한다(통합 전제).

## 4. 화면·기능 요구사항

### 사용량 통계 (`stats.html`)
1. **노드별 GPU 점유/사용량** 막대 또는 추이 차트 — **Chart.js 4.4.1 (CDN)** 사용.
2. **사용자별 사용량** 순위/집계.
3. 데이터 출처는 `usage_log`. (선택) 모니터링 job을 GET으로 읽어 현재값 보강.

### 시스템 상태 (`system.html`)
1. 노드별 카드/표: **온도(℃)** · **디스크 상태** · **NFS 연결 상태**.
2. 임계치 색상: 정상=green, 주의=orange, 위험=red (DEV_BLUEPRINT §5 색상 토큰).
3. `GET /api/system/health` 폴링 또는 새로고침으로 갱신.

## 5. 통합 제약 (★ 가장 중요)
- **노드 표기는 반드시 `node01`~`node08`.** 모니터링(팀장)·node_usage와 같은 키여야 "같은 노드"로 이어진다. 표기 어긋나면 통합이 깨짐.
- 채팅 위젯은 팀원1이 만든다. 네 `stats.html`·`system.html`에는 `<script src="/static/chat-widget.js"></script>` **한 줄만** 추가하면 플로팅 채팅이 뜬다(직접 구현 X).

## 6. 완료 기준
- [ ] `sample_health.txt` → `node_health` 적재 → 시스템 상태 화면에 온도·디스크·NFS 표시
- [ ] `usage_log` 시드 → 사용량 통계 차트 렌더(노드별·사용자별)
- [ ] 모든 노드 표기가 `node01~08`
- [ ] `stats.html`·`system.html`에 채팅 위젯 한 줄 로드로 정상 표시
- [ ] `/docs`에서 `/api/stats/*`·`/api/system/*` 단독 응답

## 7. 팀장에게 요청할 것
- `main.py`에 `stats` · `system` 라우터 2줄 등록.
- 네비에 `사용량 통계`·`시스템 상태` 링크 추가(공통 `_nav.html` → 팀장).

## 8. 바로 붙여넣는 킥오프 프롬프트
```
나는 HPC 포털 팀원2, 사용량 통계와 시스템 상태 페이지 담당이야. 첨부한 DEV_BLUEPRINT.md를 따른다.
내 소유 파일은 routers/stats.py, routers/system.py, static/stats.html, static/system.html, data/sample_health.txt 뿐(공통 파일 X).
DEV_BLUEPRINT §4 node_health/usage_log 테이블, §6 /api/stats/*·/api/system/* 엔드포인트대로:
- 사용량 통계: 노드별/사용자별 사용량 집계·추이 차트 (Chart.js 4.4.1 CDN)
- 시스템 상태: 노드별 온도·디스크·NFS 상태, 임계치 색상(green/orange/red)
node 값은 반드시 node01~node08 표기(모니터링과 연결). sample_health.txt는 'node01 temp=42 disk=OK nfs=OK' 같은 한 줄 형식으로 파싱.
stats/system.html에는 채팅 위젯을 <script src="/static/chat-widget.js"></script> 한 줄로만 포함.
디자인 토큰은 DEV_BLUEPRINT §5 준수. 각 API는 /docs에서 단독으로 응답하게.
추가 아이디어가 있으면 이 두 페이지에 얹어도 좋아.
```
