# Chạy public qua Cloudflare

## Mục tiêu
Xuất bản server phát hiện lửa ở máy này ra Internet qua Cloudflare Tunnel.

## File chính
- `chay_cloudflare_cong_khai.bat`
- `may_chu_lua.py`

## Điều kiện cần
Phải có sẵn các file sau trên máy:
- `C:\Users\Administrator\.cloudflared\bin\cloudflared.exe`
- `C:\Users\Administrator\.cloudflared\config.yml`

Tunnel ID hiện đang dùng trong script:
- `af5c2caa-5f66-4c07-89c6-afd38ad017d6`

## Cách chạy
Double-click file:
- `D:\DuAn\DoAn\server\chay_cloudflare_cong_khai.bat`

Hoặc chạy trong PowerShell:
```powershell
cd /d D:\DuAn\DoAn\server
.\chay_cloudflare_cong_khai.bat
```

## Cách kiểm tra local trước
Mở trình duyệt:
- `http://127.0.0.1:5000/api/health`
- `http://127.0.0.1:5000/api/zones`

Nếu ra JSON là server local đang ổn.

## Cách kiểm tra public
Mở:
- `https://api.khanhquan.lol/api/health`
- `https://api.khanhquan.lol/api/zones`

Nếu domain public trả JSON, client có thể dùng:
- `https://api.khanhquan.lol`

## Nếu vẫn lỗi 530
Nguyên nhân thường là:
1. Flask server local chưa chạy
2. Cloudflared chưa chạy
3. `config.yml` đang trỏ sai đích
4. DNS / route của Cloudflare đang sai

## Gợi ý debug nhanh
- test local trước bằng `127.0.0.1:5000`
- rồi mới test domain public
- nếu local chạy mà public lỗi, tập trung kiểm tra cloudflared/config.yml
