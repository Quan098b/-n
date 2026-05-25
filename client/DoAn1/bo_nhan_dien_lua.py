"""
bo_nhan_dien_lua.py
File xử lý chính của client gửi ảnh lên server.
Nhiệm vụ chính:
- quét camera khả dụng
- mở camera được chọn
- gửi frame ảnh lên server theo chu kỳ
- nhả khu khi dừng
- hỗ trợ chạy cùng Cloudflared khi dùng domain public
"""

import os
import platform
import subprocess
import threading
import time

import cv2
import requests


class BoNhanDienLua:
    """Lớp điều khiển camera client và gửi frame lên server."""

    def __init__(
        self,
        duong_dan_model="best.pt",
        chi_so_camera=0,
        kich_thuoc_anh=640,
        duong_dan_server="https://api.khanhquan.lol/api/frame"
    ):
        self.duong_dan_model = duong_dan_model
        self.chi_so_camera = chi_so_camera
        self.kich_thuoc_anh = kich_thuoc_anh
        self.duong_dan_server = duong_dan_server

        self.camera = None
        self.dang_chay = False
        self.su_kien_dung = threading.Event()

        self.ma_client = "client_01"
        self.ma_khu = None

        self.tien_trinh_cloudflared = None
        self.khoang_gui = 0.1
        self.chat_luong_jpg = 60
        self.bo_qua_frame = 1

        self.khoa_trang_thai = threading.Lock()
        self.khoa_camera = threading.Lock()

    def LayDuongDanGocServer(self):
        if self.duong_dan_server.endswith("/api/frame"):
            return self.duong_dan_server.replace("/api/frame", "")
        return self.duong_dan_server.rstrip("/")

    def LayDuongDanApiFrame(self):
        if self.duong_dan_server.endswith("/api/frame"):
            return self.duong_dan_server
        return self.duong_dan_server.rstrip("/") + "/api/frame"

    def LayDanhSachKhuTuServer(self):
        duong_dan_goc = self.LayDuongDanGocServer()
        duong_dan = duong_dan_goc + "/api/zones"

        try:
            phan_hoi = requests.get(duong_dan, timeout=8)
            phan_hoi.raise_for_status()
            return phan_hoi.json()
        except requests.HTTPError as loi:
            ma_loi = loi.response.status_code if loi.response is not None else "?"
            noi_dung = ""
            if loi.response is not None:
                try:
                    noi_dung = loi.response.text.strip()
                except Exception:
                    noi_dung = ""
            if noi_dung:
                raise RuntimeError(f"HTTP {ma_loi} từ server: {noi_dung[:300]}") from loi
            raise RuntimeError(f"HTTP {ma_loi} từ server khi hỏi danh sách khu.") from loi
        except requests.RequestException as loi:
            raise RuntimeError(f"Không kết nối được tới {duong_dan}: {loi}") from loi

    def NhaKhu(self):
        if not self.ma_khu:
            return

        try:
            duong_dan_goc = self.LayDuongDanGocServer()
            duong_dan = duong_dan_goc + f"/api/zones/{self.ma_khu}/release"
            requests.post(
                duong_dan,
                json={"client_id": self.ma_client},
                timeout=3
            )
        except Exception:
            pass

    def GanMaKhu(self, ma_khu):
        with self.khoa_trang_thai:
            if self.dang_chay:
                return False
            self.ma_khu = ma_khu
            return True

    @staticmethod
    def LayDanhSachBackendCamera():
        ten_he_dieu_hanh = platform.system().lower()

        if ten_he_dieu_hanh == "windows":
            return [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        if ten_he_dieu_hanh == "linux":
            return [cv2.CAP_V4L2, cv2.CAP_ANY]
        if ten_he_dieu_hanh == "darwin":
            return [cv2.CAP_AVFOUNDATION, cv2.CAP_ANY]
        return [cv2.CAP_ANY]

    @staticmethod
    def LietKeCameraKhaDung(chi_so_toi_da=8):
        danh_sach_camera = []
        danh_sach_backend = BoNhanDienLua.LayDanhSachBackendCamera()

        for chi_so in range(chi_so_toi_da):
            camera_hoat_dong = False

            for backend in danh_sach_backend:
                camera = cv2.VideoCapture(chi_so, backend)
                if not camera.isOpened():
                    camera.release()
                    continue

                camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

                doc_duoc, _ = camera.read()
                camera.release()

                if doc_duoc:
                    camera_hoat_dong = True
                    break

            if camera_hoat_dong:
                danh_sach_camera.append(chi_so)

        return danh_sach_camera

    def GanChiSoCamera(self, chi_so_camera):
        with self.khoa_trang_thai:
            if self.dang_chay:
                return False
            self.chi_so_camera = int(chi_so_camera)
            return True

    def DieuChinhKichThuocFrame(self, frame):
        chieu_cao, chieu_rong = frame.shape[:2]
        if chieu_rong <= self.kich_thuoc_anh:
            return frame

        ty_le = self.kich_thuoc_anh / chieu_rong
        chieu_rong_moi = int(chieu_rong * ty_le)
        chieu_cao_moi = int(chieu_cao * ty_le)
        return cv2.resize(frame, (chieu_rong_moi, chieu_cao_moi))

    def DamBaoCloudflaredDangChay(self):
        if not self.duong_dan_server.startswith("https://api.khanhquan.lol"):
            return

        if platform.system().lower() != "windows":
            return

        duong_dan_cloudflared = r"C:\Users\Administrator\.cloudflared\bin\cloudflared.exe"
        duong_dan_cau_hinh = r"C:\Users\Administrator\.cloudflared\config.yml"

        if not os.path.exists(duong_dan_cloudflared):
            return
        if not os.path.exists(duong_dan_cau_hinh):
            return
        if self.tien_trinh_cloudflared is not None and self.tien_trinh_cloudflared.poll() is None:
            return

        cau_lenh = [
            duong_dan_cloudflared,
            "tunnel",
            "--config",
            duong_dan_cau_hinh,
            "run",
            "af5c2caa-5f66-4c07-89c6-afd38ad017d6"
        ]

        self.tien_trinh_cloudflared = subprocess.Popen(
            cau_lenh,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

    def GuiFrameLenServer(self, frame):
        if not self.ma_khu:
            raise RuntimeError("Chưa chọn khu gửi ảnh.")

        frame = self.DieuChinhKichThuocFrame(frame)

        thanh_cong, anh_da_ma_hoa = cv2.imencode(
            ".jpg",
            frame,
            [cv2.IMWRITE_JPEG_QUALITY, self.chat_luong_jpg]
        )

        if not thanh_cong:
            raise RuntimeError("Không mã hóa được ảnh JPG.")

        tep_gui = {
            "image": ("frame.jpg", anh_da_ma_hoa.tobytes(), "image/jpeg")
        }
        du_lieu_gui = {
            "client_id": self.ma_client,
            "zone_id": self.ma_khu
        }

        phan_hoi = requests.post(
            self.LayDuongDanApiFrame(),
            files=tep_gui,
            data=du_lieu_gui,
            timeout=(2, 3)
        )

        if phan_hoi.status_code == 409:
            raise RuntimeError("Khu này đang bị client khác chiếm.")

        phan_hoi.raise_for_status()
        return phan_hoi.json()

    def MoCamera(self):
        danh_sach_backend = self.LayDanhSachBackendCamera()
        loi_cuoi = None

        for backend in danh_sach_backend:
            camera = cv2.VideoCapture(self.chi_so_camera, backend)
            if not camera.isOpened():
                camera.release()
                loi_cuoi = f"Backend {backend} không mở được camera {self.chi_so_camera}."
                continue

            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera.set(cv2.CAP_PROP_FPS, 30)
            camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            doc_duoc, _ = camera.read()
            if doc_duoc:
                return camera

            camera.release()
            loi_cuoi = f"Backend {backend} mở được camera nhưng không đọc được frame."

        raise RuntimeError(f"Không mở được webcam số {self.chi_so_camera}. {loi_cuoi or ''}")

    def BatDauNhanDien(self, ham_cap_nhat_trang_thai=None):
        with self.khoa_trang_thai:
            if self.dang_chay:
                return
            if not self.ma_khu:
                if ham_cap_nhat_trang_thai:
                    ham_cap_nhat_trang_thai("Chưa chọn khu.")
                return
            self.su_kien_dung.clear()
            self.dang_chay = True

        try:
            if ham_cap_nhat_trang_thai:
                ham_cap_nhat_trang_thai(f"Đang mở camera {self.chi_so_camera}...")

            camera = self.MoCamera()

            with self.khoa_camera:
                self.camera = camera

            if ham_cap_nhat_trang_thai:
                ham_cap_nhat_trang_thai(f"Đang gửi hình ảnh về khu: {self.ma_khu}")

            self.DamBaoCloudflaredDangChay()

            lan_gui_cuoi = 0
            dem_frame = 0

            while not self.su_kien_dung.is_set():
                doc_duoc, frame = camera.read()
                if not doc_duoc:
                    if ham_cap_nhat_trang_thai:
                        ham_cap_nhat_trang_thai("Không đọc được frame từ webcam.")
                    break

                dem_frame += 1
                if self.bo_qua_frame > 1 and (dem_frame % self.bo_qua_frame) != 0:
                    continue

                thoi_gian_hien_tai = time.time()
                if thoi_gian_hien_tai - lan_gui_cuoi >= self.khoang_gui:
                    lan_gui_cuoi = thoi_gian_hien_tai
                    try:
                        ket_qua = self.GuiFrameLenServer(frame)
                        if ham_cap_nhat_trang_thai:
                            ham_cap_nhat_trang_thai("")
                    except Exception as loi:
                        if ham_cap_nhat_trang_thai:
                            ham_cap_nhat_trang_thai("Mất kết nối")

        except Exception as loi:
            if ham_cap_nhat_trang_thai:
                ham_cap_nhat_trang_thai("Không mở được camera")
        finally:
            self.NhaKhu()
            self.GiaiPhongCamera()
            with self.khoa_trang_thai:
                self.dang_chay = False
                self.su_kien_dung.set()
            if ham_cap_nhat_trang_thai:
                ham_cap_nhat_trang_thai("")

    def DungNhanDien(self):
        self.su_kien_dung.set()

    def GiaiPhongCamera(self):
        with self.khoa_camera:
            if self.camera is not None:
                self.camera.release()
                self.camera = None
