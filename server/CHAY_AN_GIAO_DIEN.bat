@echo off
REM Chạy ẩn terminal Python, chỉ hiện giao diện Tkinter. Cloudflared tunnel cũng chạy ẩn từ trong may_chu_lua.py.

cd /d D:\DuAn\DoAn\server
start "" "C:\Users\Administrator\AppData\Local\Programs\Python\Python310\pythonw.exe" may_chu_lua.py
