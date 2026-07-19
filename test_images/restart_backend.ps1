$ErrorActionPreference = 'SilentlyContinue'

Write-Output "=== Zabijem stary backend ==="
$pid8000 = (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue).OwningProcess
if ($pid8000) {
  Write-Output "Kill PID $pid8000"
  Stop-Process -Id $pid8000 -Force
  Start-Sleep 2
}
$still = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($still) {
  Write-Output "STILL ALIVE: PID $($still.OwningProcess)"
} else {
  Write-Output "Port 8000 volny"
}

Write-Output ""
Write-Output "=== Spustam novy backend (cwd musi byt dental-ai/backend) ==="
Set-Location 'C:\Users\PC1\Desktop\dental-ai\backend'
Write-Output "CWD: $(Get-Location)"

# Spust uvicorn v novom okne pomocou Start-Process
$proc = Start-Process -FilePath 'cmd.exe' `
  -ArgumentList '/c', 'cd /d C:\Users\PC1\Desktop\dental-ai\backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000' `
  -WindowStyle Hidden `
  -WorkingDirectory 'C:\Users\PC1\Desktop\dental-ai\backend' `
  -PassThru
Write-Output "Started PID: $($proc.Id)"
