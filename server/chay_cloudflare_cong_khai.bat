@echo off
REM Chạy server phát hiện lửa và Cloudflared để public qua Internet.

cd /d D:\DuAn\DoAn\server

start "MayChuLua" "C:\Users\Administrator\AppData\Local\Programs\Python\Python310\python.exe" may_chu_lua.py

REM Chờ vài giây để Flask server khởi động trước khi mở tunnel.
timeout /t 4 /nobreak >nul

set CLOUDFLARED_EXE=C:\Users\Administrator\.cloudflared\bin\cloudflared.exe
set CLOUDFLARED_CONFIG=C:\Users\Administrator\.cloudflared\config.yml
set CLOUDFLARED_TUNNEL_ID=af5c2caa-5f66-4c07-89c6-afd38ad017d6

if not exist "%CLOUDFLARED_EXE%" (
    echo Khong tim thay cloudflared.exe tai: %CLOUDFLARED_EXE%
    pause
    exit /b 1
)

if not exist "%CLOUDFLARED_CONFIG%" (
    echo Khong tim thay config.yml tai: %CLOUDFLARED_CONFIG%
    pause
    exit /b 1
)

start "CloudflaredTunnel" "%CLOUDFLARED_EXE%" tunnel --config "%CLOUDFLARED_CONFIG%" run %CLOUDFLARED_TUNNEL_ID%

echo Da chay server local + Cloudflare tunnel.
echo Neu tunnel config dung, domain public se tro ve server nay.
