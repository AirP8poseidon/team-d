# 노드 푸시 에이전트 (실서버 연동)

각 계산 서버가 자기 자원 정보를 **scp 로 포털 호스트에 밀어 넣는(push)** 구조.
포털은 `COLLECTOR=ingest` 로 그 파일을 읽어 대시보드에 반영한다.

```
[각 계산 서버]  node_report.py  ──scp──▶  [포털 호스트]  data/incoming/<node>.json
                (nvidia-smi/df/nfsstat/ps)                 └ COLLECTOR=ingest 가 읽음
```

## 한 번만: 포털 호스트(받는 쪽) 준비
1. **원격 로그인(SSH) 켜기**: 시스템 설정 → 일반 → 공유 → 원격 로그인 ON. (macOS)
2. 수신 폴더 확인: `hpc-portal/data/incoming/` (없으면 `mkdir -p`).
3. 포털을 ingest 모드로 실행:
   ```bash
   cd hpc-portal && COLLECTOR=ingest uvicorn main:app --reload --port 8000
   ```
4. 포털 호스트의 **접속 정보**를 노드 쪽에 알려준다: 사용자명, IP, 수신 경로.
   현재 값 예: `user=mac-leesh  host=10.10.9.101  incoming=Develop/Projects/GEOSR_hackton/team-d/hpc-portal/data/incoming`

## 각 노드(보내는 쪽)에서
1. `node_report.py` 를 노드에 복사.
2. (권장) **무암호 SSH 키** 등록 — 비번 없이 자동 푸시:
   ```bash
   ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519      # 키 없으면
   ssh-copy-id mac-leesh@10.10.9.101                      # 포털 호스트에 공개키 등록
   ```
   (ssh-copy-id 없으면: 노드의 `~/.ssh/id_ed25519.pub` 내용을 포털의 `~/.ssh/authorized_keys` 에 추가)
3. 1회 푸시 테스트:
   ```bash
   python3 node_report.py --portal-host 10.10.9.101 --portal-user mac-leesh --node node01
   ```
4. 상시 푸시(5초 루프):
   ```bash
   python3 node_report.py --portal-host 10.10.9.101 --portal-user mac-leesh --node node01 --loop --interval 5
   ```
   또는 cron(1분 간격): `* * * * * python3 /path/node_report.py --node node01`

## 무엇을 수집하나
- GPU 사용률·온도·모델 (`nvidia-smi`), CPU·MEM (%), 디스크 상태(`df`), NFS(`mount`)
- **`mpirun` 직접 실행 작업**(`ps`) — 스케줄러 큐에 안 잡히는 것까지 잡아 Job 큐에 표시
- 도구가 없는 머신(GPU 없는 노드·맥)에서도 0/기본값으로 degrade → 그대로 동작

## 안전장치
- 깨진/없는 리포트는 건너뜀, 유효 리포트 0개면 포털이 **mock 으로 자동 폴백**(데모 안 죽음).
- `node` 값은 `node01~node08` 만 수용(통합 키 보호).
- 셀프테스트: 포털 호스트에서 `cd hpc-portal && python3 -m collectors.ingest`

## 테스트(전송 없이 JSON 만)
```bash
python3 node_report.py --node node01 --out /tmp/node01.json   # 수집 결과 확인
```
