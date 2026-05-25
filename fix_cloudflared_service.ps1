$ErrorActionPreference = "Stop"

$configPath = "C:\Users\Administrator\.cloudflared\config.yml"
$cloudflaredExe = "C:\Users\Administrator\.cloudflared\bin\cloudflared.exe"
$tunnelId = "af5c2caa-5f66-4c07-89c6-afd38ad017d6"

Write-Host "=== KIEM TRA FILE ==="
if (-not (Test-Path $configPath)) {
    Write-Error "Khong tim thay config: $configPath"
}
if (-not (Test-Path $cloudflaredExe)) {
    Write-Error "Khong tim thay cloudflared.exe: $cloudflaredExe"
}

Write-Host "=== NOI DUNG CONFIG ==="
Get-Content $configPath

Write-Host "=== VALIDATE INGRESS ==="
& $cloudflaredExe tunnel --config $configPath ingress validate

Write-Host "=== DUNG SERVICE CLOUDFLARED ==="
Stop-Service Cloudflared -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "=== GO SERVICE CU ==="
& $cloudflaredExe service uninstall
Start-Sleep -Seconds 2

Write-Host "=== CAI LAI SERVICE THEO CONFIG ==="
& $cloudflaredExe service install
Start-Sleep -Seconds 2

Write-Host "=== CHAY LAI SERVICE ==="
Start-Service Cloudflared
Start-Sleep -Seconds 6

Write-Host "=== KIEM TRA SERVICE ==="
Get-CimInstance Win32_Service -Filter "Name='Cloudflared'" |
    Select-Object Name, State, PathName, StartMode |
    Format-List

Write-Host "=== KIEM TRA TUNNEL CONNECTION ==="
try {
    & $cloudflaredExe tunnel info $tunnelId
} catch {
    Write-Host "Tunnel info loi: $($_.Exception.Message)"
}

Write-Host "=== TEST LOCAL HEALTH ==="
try {
    curl.exe -sS http://127.0.0.1:5000/api/health
} catch {
    Write-Host "Local health loi: $($_.Exception.Message)"
}

Write-Host "=== TEST PUBLIC HEALTH ==="
try {
    curl.exe -sS -i https://api.khanhquan.lol/api/health
} catch {
    Write-Host "Public health loi: $($_.Exception.Message)"
}

Write-Host "=== NEU TUNNEL CHUA CO ACTIVE CONNECTION ==="
Write-Host "Hay chay file: D:\DuAn\DoAn\run_cloudflared_with_config.bat"
Write-Host "File nay se mo cloudflared foreground dung config.yml de xem log truc tiep."
