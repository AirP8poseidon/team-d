# HANDOFF — 사무실 PC에서 이어서 작업

> 이 맥(10.10.9.101)은 HPC 클러스터와 **망이 격리**돼 직접 연동이 안 된다(양방향 timeout, git만 연결).
> 클러스터에 닿는 **사무실 PC**에서 이어서 한다. `git clone` 하면 아래 상태 그대로 복원된다.
> (submit/ 로그·증빙까지 강제 추가해 git에 전부 포함시켜 둠.)

## 받기 (사무실 PC)
```bash
git clone git@github.com:AirP8poseidon/team-d.git    # 또는 git pull
cd team-d/hpc-portal
python3 -m venv .venv && source .venv/bin/activate    # .venv·app.db 는 재생성(미포함)
pip install -r requirements.txt
```

## 지금까지 만든 것 (동작 확인됨)
- **포털**: FastAPI+SQLite, 5페이지 + 채팅 위젯. `uvicorn main:app --reload` → http://localhost:8000, `/docs`.
- **잠금 결정 1A~6A** 반영(SPEC §13): db 동시성(WAL)·멱등 시드·node_usage 최신1건·nav JS인클루드·파서 가드·pytest.
- **팀장 페이지(L1)**: `static/index.html`·`monitoring.html` 목업 디자인 + 실 API fetch(`/browse`로 픽셀 검증 완료). 단 **GPU 중심 UI**라 CPU 클러스터엔 안 맞음(아래 TODO).
- **수집 seam**: `collectors/{mock,ingest}.py`. `COLLECTOR=ingest` 면 `data/incoming/<node>.json`(또는 `HPC_INCOMING_DIR`)을 읽음. 리포트 0개면 mock 폴백.
- **노드 수집기 2종**: `agent/node_report.py`(python3·generic), **`agent/collect_node.py`(python2.7/3·이 클러스터용 — nvidia 없음·ps 상위작업 추출)**.
- **전송 스크립트**: `agent/scan_cluster.sh`(SSH 순회→incoming/scp), `agent/scan_push.sh`(git 경유), `agent/probe_server.sh`(정찰).
- **정찰 결과**: `agent/probes/*.txt` (master+node1~13 실측, 아래 요약).

## 실클러스터 실측 (agent/probes/ — 14대 균일)
- master + node1~node13. RHEL 7.9 / AMD EPYC 7543 64스레드 / 256GB.
- **python3 없음** (python 2.7만) → 노드 수집은 `collect_node.py`(py2.7) 또는 bash.
- **GPU 없음** (CPU 클러스터) → 모니터링을 **CPU/MEM + 실행 모델작업** 중심으로 바꿔야 함.
- 스케줄러 **PBS**(qstat). node12·13은 PBS 밖(직접 실행).
- 실제 작업: **pschism / padcirc / nemo / swan / Intel-MPI** (해양·폭풍해일·파랑 예보 모델). → "누가 어느 노드서 무슨 모델"이 핵심 가치.
- 노드 IP 10.10.10.x / 192.168.2.x. **이 맥(10.10.9.x)과 라우트 막힘.**

## 망 구조 결론
- 맥↔클러스터: 직접 통신 **불가**(게이트웨이 방화벽 timeout). git(GitHub)만 양쪽 연결.
- **사무실 PC가 클러스터에 닿으면** → push/scp(scan_cluster.sh `PORTAL_HOST=...`) 또는 로컬 수집 가능(실시간). 그게 안 되면 git 경유(scan_push.sh).

## 다음 할 일 (우선순위)
1. **collect_node.py 실노드 첫 실행 검증** — py2.7 노드에서 처음 도는 것. `ssh node1 "python ~/.../collect_node.py node1"` → JSON 확인.
2. **모니터링 UI를 CPU 중심으로 reframe** (가장 큰 남은 작업): 노드 카드의 GPU 막대/차트 → CPU%·MEM·현재 모델작업(사용자). Job 테이블이 주인공(pschism/padcirc/nemo/swan + user). `static/monitoring.html` 수정.
3. **노드명**: `export HPC_NODES="master,node1,...,node13"` (포털·스캐너 양쪽). db.NODES가 env로 받음.
4. **전송 방식 확정**: 사무실 PC→클러스터/맥 도달성에 따라 scp(실시간) vs git(30s). 닿으면 `scan_cluster.sh`에 `NODE_PYTHON=python AGENT=.../collect_node.py PORTAL_HOST=<포털IP>` 로.
5. 팀원 페이지(위키·채팅·통계·시스템)도 같은 CPU/모델 맥락으로.

## 로그·제출 규칙 (이어서)
- 의미 있는 단계마다 `submit/PROCESS_LOG.md`에 항목 append(현재 #1~#15까지 기록됨). 개인 사본 `submit/team-d_LeeSeongHoo_PROCESS_LOG.md` 동일 유지.
- 산출물 수정시각은 `submit/evidence/timestamps.txt`.
- repo: `git@github.com:AirP8poseidon/team-d.git` (main 브랜치 공유).
