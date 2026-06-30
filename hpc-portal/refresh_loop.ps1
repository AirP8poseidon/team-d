# 저빈도 라이브 갱신 — 이 PC에서 주기적으로 master 스캔 + incoming scp 수집.
# 포털은 5초마다 incoming/*.json 을 다시 읽으므로, scp 직후 화면에 반영된다.
# 클러스터 부하 최소화: 기본 180초 간격(읽기 전용 1회 스캔), 병렬 없음.
#
# 실행:   powershell -ExecutionPolicy Bypass -File refresh_loop.ps1            # 180초
#         powershell -ExecutionPolicy Bypass -File refresh_loop.ps1 -IntervalSec 300
# 종료:   이 창에서 Ctrl+C (또는 창 닫기)
param([int]$IntervalSec = 180)

$ErrorActionPreference = 'Continue'
$Local  = 'E:\04_Develop\Projects\GEOSR_hckt\team-d\hpc-portal\data\incoming'
$Remote = '/home/gonas/appl/probe/team-d/hpc-portal'
$Host_  = 'Geo83-gonas'

Write-Output ("refresh_loop 시작 — {0}초 간격, 대상 {1}" -f $IntervalSec, $Host_)
while ($true) {
    $t = Get-Date -Format 'HH:mm:ss'
    try {
        ssh -o BatchMode=yes -o ConnectTimeout=12 $Host_ "bash $Remote/agent/scan_once.sh > /dev/null 2>&1"
        scp -q "$($Host_):$Remote/data/incoming/*.json" "$Local\"
        $n = (Get-ChildItem "$Local\*.json" -ErrorAction SilentlyContinue).Count
        Write-Output ("[{0}] refreshed ({1} nodes)" -f $t, $n)
    } catch {
        Write-Output ("[{0}] ERROR: {1}" -f $t, $_.Exception.Message)
    }
    Start-Sleep -Seconds $IntervalSec
}
