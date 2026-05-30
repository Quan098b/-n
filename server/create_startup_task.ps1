# Tên Scheduled Task sẽ xuất hiện trong Task Scheduler của Windows.
$taskName = "FireDetectionServer"

# File .bat sẽ được Windows gọi khi người dùng đăng nhập.
$batPath = "D:\DuAn\DoAn\server\khoi_dong_may_chu.bat"

# Kiểm tra file .bat có tồn tại hay không trước khi tạo task.
if (-not (Test-Path $batPath)) {
    Write-Error "Không tìm thấy file: $batPath"
    exit 1
}

# Action = hành động sẽ chạy, ở đây là chạy file .bat.
$action = New-ScheduledTaskAction -Execute $batPath

# Trigger = thời điểm kích hoạt, ở đây là lúc đăng nhập Windows.
$trigger = New-ScheduledTaskTrigger -AtLogOn

# Settings = các tùy chọn bổ sung cho Scheduled Task.
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew

# Đăng ký hoặc ghi đè Scheduled Task vào hệ thống.
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Tự chạy server phát hiện lửa khi đăng nhập Windows" -Force

Write-Host "Đã tạo/ghi đè Scheduled Task: $taskName"
Write-Host "Chạy thử bằng lệnh: schtasks /run /tn \"$taskName\""
