# 재사용 자산 (assets) — 남이 그대로 가져다 쓸 수 있게

> 재현·전파성(25점)의 핵심. **이 폴더만 보고 다른 팀이 따라 할 수 있게** 정리했다.

## 목차
| 파일 | 무엇 |
|---|---|
| `QUICKSTART.md` | **처음 보는 사람이 10분 안에 실행하는 법** (mock·실연동·외부공개·구조) |
| `prompts.md` | 실제로 입력한 **핵심 프롬프트 모음**(단계별) + 왜 효과적이었나 |
| `DEV_BLUEPRINT.md` | 확정 스펙(역할·소유파일·DB·API·통합접점·킥오프 프롬프트) — 단일 진실 공급원 |
| `SPEC.md` | 개발 사양서(엔지니어링 잠금 6건 포함) |
| `CLAUDE_hpc-portal.md` | 앱 기술 가이드 사본(컬렉터 seam·계약·실행) — `hpc-portal/CLAUDE.md` 원본 |
| `TEAM_SYNC.md` | 팀원 필수검토 가이드(실서버 반영본: 노드명 동적·CPU·실행모드) |
| `handover/` | 팀원1·2 자기완결 핸드오버 + 붙여넣는 킥오프 프롬프트 |

## 산출물(코드) 내 재사용 포인트 (repo 안)
- **데이터 수집 seam** — `hpc-portal/collectors/` (`Collector` ABC, mock/ingest, slurm·prometheus 스텁). 데이터 소스 교체가 drop-in.
- **HPC 텔레메트리 수집기** — `hpc-portal/agent/`:
  - `collect_node.py` (py2.7 호환, CPU/MEM/디스크/NFS/온도/실행작업 1회 수집 → JSON)
  - `scan_once.sh` (master에서 전 노드 SSH 순회 → incoming, 읽기전용·1회성)
  - `probe_server.sh` (서버 제원 정찰), `node_report.py`(py3 push형), `scan_push.sh`(git 경유 전송)
- **운영 스크립트** — `hpc-portal/run_server.bat`(0.0.0.0 공개), `refresh_loop.ps1`·`run_refresh.bat`(저빈도 라이브 갱신)

## 핵심 셋업 메모
- 도구: Claude Code (`CLAUDE.md` 자동 로드). 외부도구 연동 = git(팀 공유)·SSH/scp(실서버), 서브에이전트(뼈대 스캐폴딩 #11).
- 기법: 인터뷰→청사진 1문서→팀원 핸드오버 파생 / 컬렉터 seam으로 mock·실연동 양립 / 소유파일 분리로 충돌 0 통합.
