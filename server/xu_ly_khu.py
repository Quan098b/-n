"""
xu_ly_khu.py
Module xử lý nghiệp vụ zone/khu.
Nhiệm vụ chính:
- đọc/ghi file zones.json
- thêm, xóa khu
- cập nhật độ nhạy AI cho từng khu
- kiểm tra khu còn đang được client sử dụng hay đã hết hạn timeout
- tạo dữ liệu snapshot để API và giao diện hiển thị
"""

import json
import os
import re
import time
import uuid

import trang_thai as state
from cau_hinh import CLIENT_TIMEOUT, DEFAULT_CONF_THRESHOLD, LICH_SU_PHAT_HIEN_MOI_GIAY, ZONE_FILE


def ChuanHoaDoNhay(gia_tri):
    """Ép giá trị độ nhạy AI về khoảng hợp lệ 0.05 -> 0.95."""
    gia_tri = float(gia_tri)
    if gia_tri < 0.05:
        return 0.05
    if gia_tri > 0.95:
        return 0.95
    return round(gia_tri, 2)


def ChuanHoaThoiGianLuuAnh(gia_tri):
    gia_tri = int(float(gia_tri))
    if gia_tri < 1:
        return 1
    if gia_tri > 3600:
        return 3600
    return gia_tri


def TaoMaKhu(ten_khu):
    """Tạo mã khu an toàn từ tên khu + hậu tố ngẫu nhiên."""
    # Chuẩn hóa tên để tạo ID nội bộ an toàn cho API và lưu file.
    van_ban = ten_khu.lower().strip()
    van_ban = re.sub(r"[^a-zA-Z0-9]+", "_", van_ban)
    van_ban = van_ban.strip("_")

    if not van_ban:
        van_ban = "zone"

    return f"{van_ban}_{uuid.uuid4().hex[:6]}"


def NapDanhSachKhu():
    """Nạp danh sách khu từ zones.json. Nếu chưa có file thì tạo dữ liệu mặc định."""
    if not os.path.exists(ZONE_FILE):
        du_lieu_mac_dinh = [
            {"id": "khu_1", "name": "Khu 1", "conf_threshold": DEFAULT_CONF_THRESHOLD, "history_interval": LICH_SU_PHAT_HIEN_MOI_GIAY},
            {"id": "khu_2", "name": "Khu 2", "conf_threshold": DEFAULT_CONF_THRESHOLD, "history_interval": LICH_SU_PHAT_HIEN_MOI_GIAY}
        ]

        with open(ZONE_FILE, "w", encoding="utf-8") as tep:
            json.dump(du_lieu_mac_dinh, tep, ensure_ascii=False, indent=4)

    # Đọc dữ liệu danh sách khu đã lưu từ file JSON.
    with open(ZONE_FILE, "r", encoding="utf-8") as tep:
        du_lieu = json.load(tep)

    state.zones.clear()

    for muc in du_lieu:
        ma_khu = muc["id"]
        ten_khu = muc["name"]
        nguong_tin_cay = ChuanHoaDoNhay(muc.get("conf_threshold", DEFAULT_CONF_THRESHOLD))
        thoi_gian_luu_anh = ChuanHoaThoiGianLuuAnh(muc.get("history_interval", LICH_SU_PHAT_HIEN_MOI_GIAY))

        state.zones[ma_khu] = {
            "id": ma_khu,
            "name": ten_khu,
            "client_id": None,
            "last_seen": 0,
            "time": "",
            "width": 0,
            "height": 0,
            "detections": 0,
            "conf_threshold": nguong_tin_cay,
            "history_interval": thoi_gian_luu_anh,
            "alert_until": 0
        }

    return state.zones


def LuuDanhSachKhu():
    """Lưu danh sách khu hiện tại từ memory xuống file zones.json."""
    du_lieu = []

    for khu in state.zones.values():
        du_lieu.append({
            "id": khu["id"],
            "name": khu["name"],
            "conf_threshold": ChuanHoaDoNhay(khu.get("conf_threshold", DEFAULT_CONF_THRESHOLD)),
            "history_interval": ChuanHoaThoiGianLuuAnh(khu.get("history_interval", LICH_SU_PHAT_HIEN_MOI_GIAY))
        })

    with open(ZONE_FILE, "w", encoding="utf-8") as tep:
        json.dump(du_lieu, tep, ensure_ascii=False, indent=4)


def KhuDangBiChiem(khu):
    """Kiểm tra một khu có còn đang bị client chiếm hay không."""
    ma_client = khu.get("client_id")
    lan_cuoi_nhin_thay = khu.get("last_seen", 0)

    if not ma_client:
        return False

    # timeout = quá thời gian chờ thì xem như client đã rời đi.
    if time.time() - lan_cuoi_nhin_thay > CLIENT_TIMEOUT:
        return False

    return True


def XoaTrangThaiKhuHetHan(khu):
    """Nếu client đã timeout thì xóa trạng thái chiếm khu."""
    if khu.get("client_id") and time.time() - khu.get("last_seen", 0) > CLIENT_TIMEOUT:
        khu["client_id"] = None
        khu["last_seen"] = 0


def LayAnhChupTrangThaiKhu():
    """Lấy ảnh chụp trạng thái hiện tại của toàn bộ khu để trả ra API/UI."""
    ket_qua = []

    # Duyệt toàn bộ khu để tạo dữ liệu tóm tắt trả ra giao diện/API.
    with state.state_lock:
        for khu in state.zones.values():
            XoaTrangThaiKhuHetHan(khu)
            dang_bi_chiem = KhuDangBiChiem(khu)

            ket_qua.append({
                "id": khu["id"],
                "name": khu["name"],
                "occupied": dang_bi_chiem,
                "client_id": khu["client_id"] if dang_bi_chiem else None,
                "time": khu["time"],
                "width": khu["width"],
                "height": khu["height"],
                "detections": khu["detections"],
                "conf_threshold": khu.get("conf_threshold", DEFAULT_CONF_THRESHOLD),
                "history_interval": khu.get("history_interval", LICH_SU_PHAT_HIEN_MOI_GIAY)
            })

    return ket_qua


def ThemKhu(ten_khu):
    """Tạo khu mới từ tên do người dùng nhập."""
    ten_khu = ten_khu.strip()
    if not ten_khu:
        raise ValueError("Tên khu không được để trống.")

    with state.state_lock:
        ma_khu = TaoMaKhu(ten_khu)
        state.zones[ma_khu] = {
            "id": ma_khu,
            "name": ten_khu,
            "client_id": None,
            "last_seen": 0,
            "time": "",
            "width": 0,
            "height": 0,
            "detections": 0,
            "conf_threshold": DEFAULT_CONF_THRESHOLD,
            "history_interval": LICH_SU_PHAT_HIEN_MOI_GIAY,
            "alert_until": 0
        }
        LuuDanhSachKhu()

    return ma_khu


def XoaKhu(ma_khu):
    """Xóa một khu nếu khu đó hiện không bị client nào sử dụng."""
    with state.state_lock:
        if ma_khu not in state.zones:
            raise KeyError("Không tìm thấy khu.")

        khu = state.zones[ma_khu]
        XoaTrangThaiKhuHetHan(khu)

        if KhuDangBiChiem(khu):
            raise RuntimeError("Khu này đang có client sử dụng, không thể xóa.")

        del state.zones[ma_khu]
        state.zone_frames.pop(ma_khu, None)
        state.zone_last_detect_time.pop(ma_khu, None)
        state.zone_last_history_time.pop(ma_khu, None)
        state.zone_fire_started_time.pop(ma_khu, None)
        state.zone_fire_alerted.pop(ma_khu, None)
        state.zone_last_fire_seen_time.pop(ma_khu, None)
        LuuDanhSachKhu()


def CapNhatCaiDatKhu(ma_khu, nguong_tin_cay, thoi_gian_luu_anh):
    """Cập nhật độ nhạy AI và thời gian dùng chung cho lịch sử/cảnh báo của một khu."""
    nguong_tin_cay = ChuanHoaDoNhay(nguong_tin_cay)
    thoi_gian_luu_anh = ChuanHoaThoiGianLuuAnh(thoi_gian_luu_anh)

    with state.state_lock:
        if ma_khu not in state.zones:
            raise KeyError("Không tìm thấy khu.")

        state.zones[ma_khu]["conf_threshold"] = nguong_tin_cay
        state.zones[ma_khu]["history_interval"] = thoi_gian_luu_anh
        LuuDanhSachKhu()

    return nguong_tin_cay, thoi_gian_luu_anh
