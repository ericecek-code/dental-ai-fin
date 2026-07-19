$ErrorActionPreference = 'SilentlyContinue'
Write-Output "=== Kill vsetky node/vite procesy ==="
$procs = Get-Process node,npm -ErrorAction SilentlyContinue
$killed = @()
foreach ($p in $procs) {
  $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId=$($p.Id)").CommandLine
  if ($cmd -match 'vite|npm run dev') {
    Write-Output "Kill PID $($p.Id)"
    $killed += $p.Id
    Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
  }
}

Write-Output "Killed count: $($killed.Count)"
Start-Sleep 3

Write-Output "=== Mazem Vite cache ==="
$cache1 = 'C:\Users\PC1\Desktop\dental-ai\frontend\node_modules\.vite'
$cache2 = 'C:\Users\PC1\AppData\Local\Temp\vite_*'

if (Test-Path $cache1) {
  Remove-Item -Recurse -Force $cache1 -ErrorAction SilentlyContinue
  Write-Output "Zmazany: $cache1"
} else {
  Write-Output "Cache .vite neexistuje"
}

# Vite temp
Get-ChildItem 'C:\Users\PC1\AppData\Local\Temp' -Filter 'vite_*' -ErrorAction SilentlyContinue | ForEach-Object {
  Remove-Item -Recurse -Force $_.FullName -ErrorAction SilentlyContinue
  Write-Output "Zmazany temp: $($_.FullName)"
}

# Over portu 5173
$still = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue
if ($still) {
  Write-Output "STALE PORT: PID $($still.OwningProcess) - este drzi"
  Stop-Process -Id $still.OwningProcess -Force -ErrorAction SilentlyContinue
  Start-Sleep 2
} else {
  Write-Output "Port 5173 je volny"
}

Write-Output "DONE"
