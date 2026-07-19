$ErrorActionPreference = 'SilentlyContinue'

Write-Output "=== Zabijem vsetky node/vite procesy (PC1 vlastnene) ==="
$procs = Get-Process node,npm -ErrorAction SilentlyContinue
foreach ($p in $procs) {
  $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId=$($p.Id)").CommandLine
  if ($cmd -match 'vite|npm run dev') {
    Write-Output "Kill PID $($p.Id) :: $cmd"
    Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
  }
}

Start-Sleep 3
$still = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue
if ($still) { Write-Output "STALE PORT 5173 este drzi: PID $($still.OwningProcess)" } else { Write-Output "Port 5173 volny." }

Write-Output ""
Write-Output "=== Spustam Vite znova na cisto ==="
Set-Location 'C:\Users\PC1\Desktop\dental-ai\frontend'
$out = cmd /c "npm run dev -- --host 127.0.0.1 --port 5173 --strictPort 2>&1"
Write-Output $out.Substring(0, [Math]::Min(2000, $out.Length))
