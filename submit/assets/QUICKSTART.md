# QUICKSTART — 처음 보는 사람이 10분 안에 실행하기

> 산출물: **사내 HPC 통합 포털** (FastAPI + SQLite + 정적 HTML/JS). 5페이지(홈·모니터링·정보공유·사용량통계·시스템상태) + 플로팅 채팅 위젯.
> 데이터: 기본은 샘플(mock), 옵션으로 실 HPC 클러스터(master+node1~13) 직접 수집(ingest).

## 0. 요구사항
- Python 3.10+ · `pip` · (실서버 연동 시) `ssh`/`scp` 클라이언트
- 외부 의존성 최소: `fastapi`, `uvicorn[standard]` (+ 테스트 `pytest`,`httpx`). SQLite는 표준 라이브러리.

## 1. 설치 & 실행 (mock 데이터 — 누구나 즉시)
```bash
cd hpc-portal
python -m venv .venv && . .venv/Scripts/activate    # (mac/linux: source .venv/bin/activate)
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# http://localhost:8000   ·   API 문서 /docs
```
- 시작 시 `init_db()` → `seed_if_empty()` → 컬렉터 1회 → 5초 주기 백그라운드 새로고침이 자동 실행.
- mock 모드 노드명: `node01`~`node08`.

## 2. 테스트
```bash
cd hpc-portal && pytest -q          # 13개: 파서·멱등시드·노드키·라우터 스모크·팀원 기능
```

## 3. 실 HPC 클러스터 연동 (ingest) — 선택
실서버에서 자원/작업/온도를 수집해 표시한다. 토폴로지: **포털PC ↔ master ↔ 각 노드**.
```bash
# (A) master 에서 1회 스캔 → data/incoming/<node>.json 생성 (읽기전용)
ssh <master> "bash <repo>/hpc-portal/agent/scan_once.sh"
# (B) 포털PC 로 수집물 가져오기
scp "<master>:<repo>/hpc-portal/data/incoming/*.json" hpc-portal/data/incoming/
# (C) ingest 모드로 포털 실행 (실노드명 주입)
set HPC_NODES=master,node1,node2,...,node13      # (mac/linux: export)
set COLLECTOR=ingest
uvicorn main:app --host 0.0.0.0 --port 8000
```
- 라이브 갱신: `hpc-portal/refresh_loop.ps1`(저빈도 180초 스캔+scp) 또는 `run_refresh.bat`.
- 원클릭 서버: `hpc-portal/run_server.bat` (0.0.0.0:8000 · ingest).

## 4. 외부(사무실 LAN) 공개
```powershell
# 관리자 PowerShell — 같은 대역만 허용
New-NetFirewallRule -DisplayName "HPC Portal 8000" -Direction Inbound -Action Allow `
  -Protocol TCP -LocalPort 8000 -Profile Any -RemoteAddress <대역>/24
```
접속: `http://<포털PC IP>:8000`  ·  보안: 인증 없음 → **신뢰된 LAN 데모 전용**.

## 5. 구조 한눈에
```
hpc-portal/
  main.py            앱 진입점(라우터 5개 등록·정적 서빙·5초 컬렉터)
  db.py              SQLite 연결·테이블·시드 (NODES 통합키)
  collectors/        수집 seam: mock(샘플파싱) / ingest(incoming json) / slurm·prometheus(스텁)
  routers/           monitoring·wiki·chat·stats·system (각자 /api/<area>)
  static/            5페이지 + chat-widget.js + _nav.html(사이드바)+theme.css
  agent/             실서버 수집: collect_node.py(py2.7)·scan_once.sh·probe_server.sh
  data/              sample_*.txt(mock) · incoming/(실수집)
  tests/             pytest 13
```
자세한 아키텍처·계약은 `hpc-portal/CLAUDE.md`(= assets/CLAUDE_hpc-portal.md) 참고.
