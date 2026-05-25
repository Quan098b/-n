$taskName = "FireSmokeStartAll"
$batPath = "D:\DuAn\DoAn\start_all.bat"

if (-not (Test-Path $batPath)) {
    Write-Error "Không tìm thấy file: $batPath"
    exit 1
}

$action = New-ScheduledTaskAction -Execute $batPath
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Tự mở server + client fire/smoke khi đăng nhập Windows" -Force

Write-Host "Đã tạo/ghi đè Scheduled Task: $taskName"
Write-Host "Chạy thử bằng lệnh: schtasks /run /tn \"$taskName\""
