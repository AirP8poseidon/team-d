# Run — HPC 포털 실행 스크립트

포털을 **더블클릭 한 번**으로 띄우는 실행 파일 모음입니다. (Windows `.bat` / mac·linux `.sh`)

## 📁 파일 목록
| 파일 | 용도 |
|---|---|
| `setup.bat` / `setup.sh` | **최초 1회** — 가상환경(.venv) + 의존성 설치 |
| `start_server_mock.bat` | 서버 실행 **(mock 데이터)** — 클러스터 없이 **어디서나** 동작. 채점·체험용 |
| `start_server.bat` | 서버 실행 **(ingest 실데이터)** — 실 클러스터 연동. **데모 PC 전용**(SSH 접근 필요) |
| `start_refresh.bat` | **라이브 갱신 루프** (180초마다 클러스터 스캔 → 반영). ingest 모드일 때만 |
| `stop.bat` | 서버 + 갱신 루프 **종료** |
| `start_server.sh` | mac/linux 서버 실행 (기본 mock, `COLLECTOR=ingest`로 실데이터) |

## 🚀 빠른 시작 (Windows)

### 1) 최초 1회 설치
```
setup.bat  더블클릭
```
(Python 3.10+ 필요. `.venv` 생성 + `pip install`)

### 2) 서버 실행 — 둘 중 하나
- **체험/채점(클러스터 없이)**: `start_server_mock.bat` 더블클릭
- **실 클러스터 데모**: `start_server.bat` 더블클릭 (SSH 별칭 `Geo83-gonas` 접근 가능한 PC에서)

→ 브라우저에서 **http://localhost:8000**
→ 다른 PC(같은 LAN): **http://<이 PC IP>:8000**  (IP 확인: `ipconfig`)

### 3) (실데이터일 때) 라이브 갱신
별도 창에서 `start_refresh.bat` 더블클릭 → 180초마다 자동 갱신.

### 4) 종료
`stop.bat` 더블클릭 (서버 + 갱신 루프 모두 종료)

## 🌐 외부(사무실 LAN) 공개 — 최초 1회, 관리자
기본은 이 PC(localhost)에서만 보입니다. 다른 PC에서 접속하려면 **관리자 PowerShell**에서:
```powershell
New-NetFirewallRule -DisplayName "HPC Portal 8000" -Direction Inbound -Action Allow `
  -Protocol TCP -LocalPort 8000 -Profile Any -RemoteAddress <내대역>/24
```
(예: `10.27.1.0/24`) — 같은 사무실 대역만 허용. **인증 없음이라 신뢰된 LAN 데모 전용.**

## 🍎 mac / linux
```bash
./setup.sh                    # 최초 1회
./start_server.sh             # mock 실행
COLLECTOR=ingest ./start_server.sh   # 실데이터 실행
```

## ℹ️ 참고
- 모드: `mock`=샘플데이터(node01~08) / `ingest`=실 클러스터(master,node1~13, `data/incoming/*.json` 읽음)
- 실데이터 수집 파이프라인·구조는 `../hpc-portal/CLAUDE.md`, 10분 가이드는 `../submit/assets/QUICKSTART.md` 참고.
