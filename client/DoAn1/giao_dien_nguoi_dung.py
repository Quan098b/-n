"""
giao_dien_client.py
Giao diện desktop Tkinter cho client gửi ảnh.
Nhiệm vụ chính:
- chọn server đích
- quét và chọn camera
- hỏi server để lấy danh sách khu trống
- bắt đầu/dừng gửi ảnh từ camera lên server
- hiển thị trạng thái hoạt động của client
"""

import threading
import tkinter as tk
from tkinter import ttk

from bo_nhan_dien_lua import BoNhanDienLua


class GiaoDienNhanDien:
    """Giao diện điều khiển client gửi ảnh lên server để phát hiện lửa."""

    def __init__(self, cua_so_goc):
        self.cua_so_goc = cua_so_goc
        self.cua_so_goc.title("Client gửi ảnh phát hiện lửa")
        self.cua_so_goc.geometry("540x400")
        self.cua_so_goc.resizable(False, False)

        # Tạo đối tượng xử lý chính để mở camera và gửi ảnh lên server.
        self.bo_nhan_dien = BoNhanDienLua(
            duong_dan_model="best.pt",
            chi_so_camera=0,
            kich_thuoc_anh=640,
            duong_dan_server="https://api.khanhquan.lol/api/frame"
        )

        self.luong_nhan_dien = None
        self.dang_nhan_dien = False
        self.dang_dung = False
        self.dang_dong_cua_so = False

        self.ban_do_khu = {}

        self.TaoThanhPhanGiaoDien()
        self.LamMoiDanhSachCamera()
        self.LamMoiDanhSachKhu()

        # Gán sự kiện bấm nút X của cửa sổ cho hàm tự xử lý đóng an toàn.
        self.cua_so_goc.protocol("WM_DELETE_WINDOW", self.XuLyDongCuaSo)

    def TaoThanhPhanGiaoDien(self):
        nhan_tieu_de = tk.Label(self.cua_so_goc, text="CLIENT GỬI ẢNH PHÁT HIỆN LỬA", font=("Arial", 14, "bold"))
        nhan_tieu_de.pack(pady=12)

        khung_camera = tk.Frame(self.cua_so_goc)
        khung_camera.pack(pady=5)

        tk.Label(khung_camera, text="Camera:", font=("Arial", 11)).grid(row=0, column=0, padx=5)

        self.hop_chon_camera = ttk.Combobox(khung_camera, width=18, state="readonly")
        self.hop_chon_camera.grid(row=0, column=1, padx=5)

        self.nut_lam_moi_camera = tk.Button(khung_camera, text="Làm mới camera", font=("Arial", 10), command=self.LamMoiDanhSachCamera)
        self.nut_lam_moi_camera.grid(row=0, column=2, padx=5)

        khung_khu = tk.Frame(self.cua_so_goc)
        khung_khu.pack(pady=5)

        tk.Label(khung_khu, text="Khu gửi ảnh:", font=("Arial", 11)).grid(row=0, column=0, padx=5)

        self.hop_chon_khu = ttk.Combobox(khung_khu, width=26, state="readonly")
        self.hop_chon_khu.grid(row=0, column=1, padx=5)

        self.nut_lam_moi_khu = tk.Button(khung_khu, text="Hỏi server", font=("Arial", 10), command=self.LamMoiDanhSachKhu)
        self.nut_lam_moi_khu.grid(row=0, column=2, padx=5)

        self.nhan_thong_tin_khu = tk.Label(self.cua_so_goc, text="", font=("Arial", 10), fg="#374151")
        self.nhan_thong_tin_khu.pack(pady=2)

        self.nut_bat_dau_dung = tk.Button(
            self.cua_so_goc,
            text="Bắt đầu phát hiện lửa",
            font=("Arial", 12, "bold"),
            width=24,
            height=2,
            bg="#2e7d32",
            fg="white",
            command=self.ChuyenTrangThaiNhanDien
        )
        self.nut_bat_dau_dung.pack(pady=18)

        self.nhan_trang_thai = tk.Label(self.cua_so_goc, text="", font=("Arial", 10), fg="blue", wraplength=500, justify="center")
        self.nhan_trang_thai.pack(pady=5)

    def ApDungDuongDanServer(self):
        duong_dan_goc = "https://api.khanhquan.lol"

        # Ghép thêm /api/frame để client gửi ảnh đúng endpoint của server.
        self.bo_nhan_dien.duong_dan_server = duong_dan_goc + "/api/frame"

    def LamMoiDanhSachCamera(self):
        if self.dang_nhan_dien:
            return

        self.hop_chon_camera.config(state="disabled")
        self.nut_lam_moi_camera.config(state="disabled")
        self.hop_chon_camera["values"] = ["Đang quét camera..."]
        self.hop_chon_camera.current(0)
        self.CapNhatTrangThai("Đang quét camera...")

        # Tạo luồng nền để quét camera mà không làm treo giao diện.
        luong = threading.Thread(target=self.QuetCameraNen, daemon=True)
        luong.start()

    def QuetCameraNen(self):
        try:
            danh_sach_camera = BoNhanDienLua.LietKeCameraKhaDung(chi_so_toi_da=8)
        except Exception:
            danh_sach_camera = []

        # Đưa việc cập nhật giao diện về luồng chính của Tkinter.
        self.cua_so_goc.after(0, lambda: self.ApDungDanhSachCamera(danh_sach_camera))

    def ApDungDanhSachCamera(self, danh_sach_camera):
        if self.dang_dong_cua_so:
            return

        if len(danh_sach_camera) == 0:
            danh_sach_camera = [0]
            self.CapNhatTrangThai("Không tự quét được camera. Tạm dùng Camera 0.")

        gia_tri_hien_thi = [f"Camera {chi_so_camera}" for chi_so_camera in danh_sach_camera]

        # Đưa danh sách camera tìm được lên hộp chọn.
        self.hop_chon_camera["values"] = gia_tri_hien_thi
        self.hop_chon_camera.current(0)
        self.hop_chon_camera.config(state="readonly")
        self.nut_lam_moi_camera.config(state="normal")

        self.CapNhatTrangThai(f"Đã tìm thấy {len(danh_sach_camera)} camera.")

    def LayChiSoCameraDangChon(self):
        gia_tri = self.hop_chon_camera.get()

        try:
            # Tách số camera từ chuỗi hiển thị như "Camera 0".
            return int(gia_tri.replace("Camera", "").strip())
        except Exception:
            return 0

    def LamMoiDanhSachKhu(self):
        if self.dang_nhan_dien:
            return

        self.ApDungDuongDanServer()

        self.hop_chon_khu.config(state="disabled")
        self.nut_lam_moi_khu.config(state="disabled")
        self.hop_chon_khu["values"] = ["Đang hỏi server..."]
        self.hop_chon_khu.current(0)
        self.nhan_thong_tin_khu.config(text="Đang hỏi server có khu nào trống...")

        # Tạo luồng nền để hỏi server mà không làm đứng giao diện.
        luong = threading.Thread(target=self.QuetKhuNen, daemon=True)
        luong.start()

    def QuetKhuNen(self):
        loi = None
        try:
            du_lieu = self.bo_nhan_dien.LayDanhSachKhuTuServer()
            danh_sach_khu = du_lieu.get("zones", [])
        except Exception as exc:
            danh_sach_khu = []
            loi = str(exc)

        # Đưa việc cập nhật danh sách khu về luồng chính của Tkinter.
        self.cua_so_goc.after(0, lambda ds=danh_sach_khu, err=loi: self.ApDungDanhSachKhu(ds, err))

    def ApDungDanhSachKhu(self, danh_sach_khu, loi=None):
        if self.dang_dong_cua_so:
            return

        self.ban_do_khu.clear()

        if loi:
            thong_bao_loi = str(loi)
            self.hop_chon_khu["values"] = []
            self.hop_chon_khu.config(state="readonly")
            self.nut_lam_moi_khu.config(state="normal")
            self.nhan_thong_tin_khu.config(text="Không kết nối được")
            self.CapNhatTrangThai("Không kết nối được")
            return

        danh_sach_khu_trong = []
        so_khu_ban = 0

        for khu in danh_sach_khu:
            if khu.get("occupied"):
                so_khu_ban += 1
                continue

            ten_hien_thi = str(khu.get("name", "")).strip()
            if not ten_hien_thi:
                ten_hien_thi = "Khu"

            # Lưu tên hiển thị để người dùng chọn, nhưng vẫn giữ ID thật để gửi lên server.
            self.ban_do_khu[ten_hien_thi] = khu.get("id")
            danh_sach_khu_trong.append(ten_hien_thi)

        if len(danh_sach_khu_trong) == 0:
            self.hop_chon_khu["values"] = []
            self.nhan_thong_tin_khu.config(text="Hết chỗ")
        else:
            self.hop_chon_khu["values"] = danh_sach_khu_trong
            self.hop_chon_khu.current(0)
            self.nhan_thong_tin_khu.config(text="")

        # Mở lại hộp chọn và nút làm mới sau khi đã lấy xong dữ liệu từ server.
        self.hop_chon_khu.config(state="readonly")
        self.nut_lam_moi_khu.config(state="normal")

        self.CapNhatTrangThai("")

    def LayMaKhuDangChon(self):
        ten_hien_thi = self.hop_chon_khu.get()
        return self.ban_do_khu.get(ten_hien_thi)

    def CapNhatTrangThai(self, thong_bao):
        if self.dang_dong_cua_so:
            return

        try:
            if thong_bao:
                self.cua_so_goc.after(0, lambda: self.nhan_trang_thai.config(text=thong_bao))
            else:
                self.cua_so_goc.after(0, lambda: self.nhan_trang_thai.config(text=""))
        except Exception:
            pass

    def ChuyenTrangThaiNhanDien(self):
        if self.dang_dung:
            return

        if not self.dang_nhan_dien:
            self.BatDauNhanDien()
        else:
            self.DungNhanDien()

    def BatDauNhanDien(self):
        self.ApDungDuongDanServer()

        chi_so_camera = self.LayChiSoCameraDangChon()
        ma_khu = self.LayMaKhuDangChon()

        if not ma_khu:
            self.CapNhatTrangThai("Chưa chọn được khu")
            return

        # Gán camera và khu đã chọn cho bộ xử lý client.
        self.bo_nhan_dien.GanChiSoCamera(chi_so_camera)
        self.bo_nhan_dien.GanMaKhu(ma_khu)

        self.dang_nhan_dien = True
        self.dang_dung = False

        self.hop_chon_camera.config(state="disabled")
        self.hop_chon_khu.config(state="disabled")
        self.nut_lam_moi_camera.config(state="disabled")
        self.nut_lam_moi_khu.config(state="disabled")

        self.nut_bat_dau_dung.config(text="Dừng phát hiện lửa", bg="#c62828", state="normal")
        self.CapNhatTrangThai("Đang chạy...")

        # Tạo luồng nền để việc gửi ảnh chạy song song với giao diện.
        self.luong_nhan_dien = threading.Thread(target=self.ChayNhanDienNen, daemon=True)
        self.luong_nhan_dien.start()

    def ChayNhanDienNen(self):
        try:
            self.bo_nhan_dien.BatDauNhanDien(ham_cap_nhat_trang_thai=self.CapNhatTrangThai)
        finally:
            # Khi luồng gửi ảnh kết thúc, quay về luồng chính để cập nhật giao diện.
            self.cua_so_goc.after(0, self.XuLySauKhiDungNhanDien)

    def DungNhanDien(self):
        self.dang_dung = True
        self.nut_bat_dau_dung.config(text="Đang dừng...", state="disabled", bg="#757575")
        self.CapNhatTrangThai("Đang dừng...")
        self.bo_nhan_dien.DungNhanDien()

    def XuLySauKhiDungNhanDien(self):
        if self.dang_dong_cua_so:
            self.DongCuaSoAnToan()
            return

        self.dang_nhan_dien = False
        self.dang_dung = False

        self.hop_chon_camera.config(state="readonly")
        self.hop_chon_khu.config(state="readonly")
        self.nut_lam_moi_camera.config(state="normal")
        self.nut_lam_moi_khu.config(state="normal")

        self.nut_bat_dau_dung.config(text="Bắt đầu phát hiện lửa", bg="#2e7d32", state="normal")

        self.CapNhatTrangThai("Đã dừng")
        self.LamMoiDanhSachKhu()

    def XuLyDongCuaSo(self):
        self.dang_dong_cua_so = True
        # Ra lệnh dừng luồng gửi ảnh trước khi đóng cửa sổ.
        self.bo_nhan_dien.DungNhanDien()

        if self.luong_nhan_dien is not None and self.luong_nhan_dien.is_alive():
            self.KiemTraLuongTruocKhiDong()
        else:
            self.DongCuaSoAnToan()

    def KiemTraLuongTruocKhiDong(self):
        if self.luong_nhan_dien is not None and self.luong_nhan_dien.is_alive():
            self.cua_so_goc.after(100, self.KiemTraLuongTruocKhiDong)
        else:
            self.DongCuaSoAnToan()

    def DongCuaSoAnToan(self):
        try:
            self.cua_so_goc.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    cua_so_goc = tk.Tk()
    ung_dung = GiaoDienNhanDien(cua_so_goc)
    cua_so_goc.mainloop()
