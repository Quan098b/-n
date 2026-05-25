@echo off
setlocal
chcp 65001 >nul

set "THU_MUC_GOC=D:\DuAn\DoAn"
set "THU_MUC_SERVER=%THU_MUC_GOC%\server"
set "PYTHON_EXE=C:\Users\Administrator\AppData\Local\Programs\Python\Python310\python.exe"
set "CLOUDFLARED_EXE=C:\Users\Administrator\.cloudflared\bin\cloudflared.exe"
set "CLOUDFLARED_CONFIG=C:\Users\Administrator\.cloudflared\config.yml"
set "TUNNEL_ID=af5c2caa-5f66-4c07-89c6-afd38ad017d6"
set "TEN_MIEN=api.khanhquan.lol"

echo ==============================================
echo   KHOI DONG SERVER + HTTPS TUNNEL CLOUDFLARE
echo ==============================================
echo.

if not exist "%PYTHON_EXE%" (
    echo [LOI] Khong tim thay Python: %PYTHON_EXE%
    pause
    exit /b 1
)

if not exist "%CLOUDFLARED_EXE%" (
    echo [LOI] Khong tim thay cloudflared: %CLOUDFLARED_EXE%
    pause
    exit /b 1
)

if not exist "%CLOUDFLARED_CONFIG%" (
    echo [LOI] Khong tim thay file config Cloudflared: %CLOUDFLARED_CONFIG%
    pause
    exit /b 1
)

echo [1/3] Dong cloudflared cu neu con dang chay...
taskkill /IM cloudflared.exe /F >nul 2>&1

echo [2/3] Lam moi DNS route cho %TEN_MIEN% ...
"%CLOUDFLARED_EXE%" tunnel route dns %TUNNEL_ID% %TEN_MIEN%
if errorlevel 1 (
    echo [LOI] Khong tao/lam moi duoc DNS route cho %TEN_MIEN%
    pause
    exit /b 1
)

echo.
echo [3/3] Mo server va tunnel...
start "Server Giam Sat Chay Khoi" cmd /k "cd /d "%THU_MUC_SERVER%" && "%PYTHON_EXE%" chay_server.py"
timeout /t 4 >nul
start "HTTPS Tunnel Cloudflare" cmd /k ""%CLOUDFLARED_EXE%" tunnel --config "%CLOUDFLARED_CONFIG%" run %TUNNEL_ID%"

echo.
echo Da bat server va HTTPS tunnel.
echo Neu client chay cung may, van nhap server la: https://api.khanhquan.lol
echo.
pause
endlocal
