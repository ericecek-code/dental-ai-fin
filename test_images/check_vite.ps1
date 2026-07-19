$ErrorActionPreference = 'SilentlyContinue'

Write-Output "=== Proces na 5173 ==="
$pid5173 = (Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue).OwningProcess
if ($pid5173) {
  Write-Output "PID: $pid5173"
  Get-Process -Id $pid5173 -ErrorAction SilentlyContinue | Format-List Id,ProcessName
  Get-CimInstance Win32_Process -Filter "ProcessId=$pid5173" | Select-Object CommandLine | Format-List
} else {
  Write-Output "Ziaden proces nepozera 5173"
}

Write-Output ""
Write-Output "=== Vsetky child procesy npm/node (vlastnik je PC1) ==="
Get-Process node,npm -ErrorAction SilentlyContinue | Where-Object { $_.SessionId -eq (Get-Process -Id $PID).SessionId } | ForEach-Object {
  Write-Output "PID $($_.Id) RAM $([math]::Round($_.WorkingSet64/1MB,1))MB :: $((Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine)"
}

Write-Output ""
Write-Output "=== Test port 5173 ==="
try {
  $r = Invoke-WebRequest -Uri 'http://127.0.0.1:5173/' -UseBasicParsing -TimeoutSec 5
  Write-Output "HTTP: $($r.StatusCode)"
  Write-Output "First 300: $($r.Content.Substring(0,[Math]::Min(300,$r.Content.Length)))"
} catch {
  Write-Output "ERR: $($_.Exception.Message)"
}
