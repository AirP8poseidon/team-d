# 서버 정찰 결과 모음

각 원격 서버가 `probe_server.sh` 출력을 `<hostname>.txt` 로 저장해 git push 하는 곳.
포털 담당(팀장)이 이 파일들을 받아 `node_report.py`·`db.NODES` 를 실제 제원에 맞게 조정한다.

저장 규칙: 파일명 = 서버 hostname(`hostname -s`). 예: `gpu01.txt`, `cpu-farm.txt`.
