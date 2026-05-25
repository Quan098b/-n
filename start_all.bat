@echo off
start "FireSmoke Server" cmd /k "cd /d D:\DuAn\DoAn\server && \"C:\Users\Administrator\AppData\Local\Programs\Python\Python310\python.exe\" server.py"
timeout /t 3 >nul
start "Cloudflared Tunnel" cmd /k "cd /d C:\Users\Administrator\.cloudflared && \"C:\Users\Administrator\.cloudflared\bin\cloudflared.exe\" tunnel --config \"C:\Users\Administrator\.cloudflared\config.yml\" run af5c2caa-5f66-4c07-89c6-afd38ad017d6"
timeout /t 5 >nul
start "FireSmoke Client" cmd /k "cd /d D:\DuAn\DoAn\client\DoAn1 && \"C:\Users\Administrator\AppData\Local\Programs\Python\Python310\python.exe\" gui_app.py"
