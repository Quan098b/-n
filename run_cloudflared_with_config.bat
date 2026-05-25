@echo off
cd /d C:\Users\Administrator\.cloudflared
"C:\Users\Administrator\.cloudflared\bin\cloudflared.exe" tunnel --config "C:\Users\Administrator\.cloudflared\config.yml" run af5c2caa-5f66-4c07-89c6-afd38ad017d6
pause
