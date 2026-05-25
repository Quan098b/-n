# Chạy ẩn terminal

## Mục tiêu
- Không hiện cửa sổ terminal Python
- Không hiện cửa sổ Cloudflared tunnel
- Chỉ hiện giao diện desktop Tkinter của server

## Cách chạy
Double-click file:
- `CHAY_AN_GIAO_DIEN.bat`

Hoặc chạy trong terminal:
```powershell
cd /d D:\DuAn\DoAn\server
.\CHAY_AN_GIAO_DIEN.bat
```

## Cách hoạt động
- `CHAY_AN_GIAO_DIEN.bat` gọi `pythonw.exe may_chu_lua.py`
- `may_chu_lua.py` tự mở Cloudflared tunnel ở chế độ ẩn
- Flask server chạy nền trong tiến trình Python GUI
- chỉ còn giao diện Tkinter hiện ra trên màn hình

## Lưu ý
Nếu app không hiện gì, kiểm tra:
- `pythonw.exe` có tồn tại không
- `cloudflared.exe` có tồn tại không
- `config.yml` của Cloudflared có đúng không
