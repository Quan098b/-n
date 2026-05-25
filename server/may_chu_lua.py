"""
chay_server.py
File khởi động chính của hệ thống server.
Nhiệm vụ:
- tạo ứng dụng Flask
- nạp dữ liệu zone ban đầu
- nạp model YOLO
- đăng ký HTTP routes
- chạy web server ở background thread
- mở luôn giao diện desktop Tkinter khi chạy file này
"""

import os
import subprocess
import threading
import tkinter as tk

from flask import Flask

from cau_hinh import HOST, PORT
from giao_dien_server import App as UngDungGiaoDienServer
from xu_ly_model import NapModel
from dinh_tuyen_api import DangKyRoutes
from xu_ly_khu import NapDanhSachKhu
from xu_ly_am_thanh import DungCanhBaoAmThanh
from xu_ly_thong_bao_day import NapTokenDiDongDaLuu

# Tạo ứng dụng Flask trung tâm để nhận API từ client và phục vụ web.
ung_dung = Flask(__name__)

# Gắn toàn bộ route/API vào ứng dụng Flask.
DangKyRoutes(ung_dung)


def ChayCloudflaredTunnel():
    duong_dan_cloudflared = r"C:\Users\Administrator\.cloudflared\bin\cloudflared.exe"
    duong_dan_cau_hinh = r"C:\Users\Administrator\.cloudflared\config.yml"
    tunnel_id = "af5c2caa-5f66-4c07-89c6-afd38ad017d6"

    if not os.path.exists(duong_dan_cloudflared):
        print(f"[WARN] Không tìm thấy cloudflared.exe: {duong_dan_cloudflared}")
        return None

    if not os.path.exists(duong_dan_cau_hinh):
        print(f"[WARN] Không tìm thấy config.yml: {duong_dan_cau_hinh}")
        return None

    try:
        print("[INFO] Đang khởi động Cloudflared tunnel...")
        startupinfo = None
        creationflags = 0

        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = subprocess.CREATE_NO_WINDOW

        return subprocess.Popen([
            duong_dan_cloudflared,
            "tunnel",
            "--config",
            duong_dan_cau_hinh,
            "run",
            tunnel_id
        ], startupinfo=startupinfo, creationflags=creationflags)
    except Exception as loi:
        print(f"[WARN] Không khởi động được Cloudflared tunnel: {loi}")
        return None


def ChayFlaskServer():
    # Tạo luồng nền để Flask chạy song song với giao diện Tkinter.
    print("[INFO] Khoi dong server API...")
    print(f"[INFO] Local: http://127.0.0.1:{PORT}")
    print(f"[INFO] LAN:   http://<IP-MAY-SERVER>:{PORT}")
    print("[INFO] Trang web: /")
    print("[INFO] API nhan anh: POST /api/frame")
    print("[INFO] Danh sach khu: GET /api/zones")
    print("[INFO] Cai dat khu: GET/POST /api/zones/<zone_id>/settings")
    print("[INFO] MJPEG stream: GET /stream/<zone_id>")

    ung_dung.run(host=HOST, port=PORT, debug=False, threaded=True, use_reloader=False)


def MoGiaoDienDesktop():
    # Tạo cửa sổ gốc của Tkinter để hiển thị giao diện quản lý server.
    cua_so_goc = tk.Tk()
    UngDungGiaoDienServer(cua_so_goc)

    # mainloop = vòng lặp chính của giao diện, giúp cửa sổ luôn phản hồi.
    cua_so_goc.mainloop()


if __name__ == "__main__":
    # Nạp danh sách khu trước để server có dữ liệu ban đầu.
    NapDanhSachKhu()
    NapTokenDiDongDaLuu()

    tien_trinh_cloudflared = ChayCloudflaredTunnel()

    try:
        # Nạp model AI ngay lúc khởi động để sẵn sàng nhận ảnh từ client.
        NapModel()
        print("[INFO] Đã nạp model YOLO nhận diện lửa thành công.")
    except Exception as loi:
        print(f"[WARN] Không nạp được model YOLO nhận diện lửa: {loi}")

    # Tạo luồng nền để Flask server không chặn giao diện Tkinter.
    luong_server = threading.Thread(target=ChayFlaskServer, daemon=True)
    luong_server.start()

    try:
        # Chạy giao diện quản lý server ở luồng chính.
        MoGiaoDienDesktop()
    finally:
        DungCanhBaoAmThanh()
        if tien_trinh_cloudflared is not None:
            try:
                tien_trinh_cloudflared.terminate()
            except Exception:
                pass
