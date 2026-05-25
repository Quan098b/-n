@echo off
powershell -Command "Start-Process PowerShell -ArgumentList '-ExecutionPolicy Bypass -File ""D:\DuAn\DoAn\fix_cloudflared_service.ps1""' -Verb RunAs"
