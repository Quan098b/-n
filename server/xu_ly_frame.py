"""
xu_ly_frame.py
Module xử lý frame ảnh theo từng khu.
Nhiệm vụ chính:
- nhận frame mới từ client
- quyết định khi nào cần chạy AI để giảm tải
- mã hóa JPG
- tạo luồng MJPEG cho web/giao diện
- sinh ảnh placeholder khi chưa có dữ liệu
"""

import time
from datetime import datetime

import cv2
import numpy as np

import trang_thai as state
from cau_hinh import DEFAULT_CONF_THRESHOLD, DETECTION_MIN_INTERVAL, JPEG_QUALITY, STREAM_SLEEP, LICH_SU_PHAT_HIEN_MOI_GIAY
from xu_ly_model import NhanDienLua
from xu_ly_khu import ChuanHoaDoNhay, KhuDangBiChiem, XoaTrangThaiKhuHetHan
from xu_ly_lich_su import GhiLichSuKhu
from xu_ly_am_thanh import BatBaoDongChoKhu, CapNhatCanhBaoAmThanh, TatBaoDongChoKhu
from xu_ly_thong_bao_day import GuiCanhBaoDayDenDienThoai


THOI_GIAN_CHO_PHEP_ROT_DETECTION_GIAY = 1.0


def LayThoiGianDangChuoi():
    # Chuyển thời gian hiện tại sang chuỗi để lưu và hiển thị.
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def CapNhatFrameChoKhu(ma_khu, frame, ma_client="local_client", co_chay_nhan_dien=True):
    """Cập nhật frame mới cho một khu và chạy AI nếu tới ngưỡng thời gian cho phép."""
    # Dùng khóa để tránh nhiều luồng cùng sửa dữ liệu khu một lúc.
    with state.state_lock:
        if ma_khu not in state.zones:
            raise KeyError("Khu không tồn tại.")

        khu = state.zones[ma_khu]
        XoaTrangThaiKhuHetHan(khu)

        # Không cho client khác ghi đè vào khu đang bị chiếm.
        if KhuDangBiChiem(khu) and khu.get("client_id") != ma_client:
            raise RuntimeError("Khu này đang bị client khác chiếm.")

        ban_sao_khu_cu = dict(khu)
        frame_cu = state.zone_frames.get(ma_khu)
        thoi_diem_nhan_dien_cuoi = state.zone_last_detect_time.get(ma_khu, 0)
        nguong_tin_cay = ChuanHoaDoNhay(khu.get("conf_threshold", DEFAULT_CONF_THRESHOLD))

    if frame is None:
        raise ValueError("Frame đầu vào không hợp lệ.")

    thoi_gian_hien_tai = time.time()

    # Chỉ chạy AI lại khi đã qua một khoảng thời gian tối thiểu để giảm tải máy.
    co_nen_chay_nhan_dien = co_chay_nhan_dien and (
        frame_cu is None or thoi_gian_hien_tai - thoi_diem_nhan_dien_cuoi >= DETECTION_MIN_INTERVAL
    )

    if co_nen_chay_nhan_dien:
        frame_da_ve, so_luong_phat_hien = NhanDienLua(frame, nguong_tin_cay)
        state.zone_last_detect_time[ma_khu] = thoi_gian_hien_tai

        thoi_gian_dung_chung = int(ban_sao_khu_cu.get("history_interval", LICH_SU_PHAT_HIEN_MOI_GIAY) or LICH_SU_PHAT_HIEN_MOI_GIAY)

        if so_luong_phat_hien > 0:
            state.zone_last_fire_seen_time[ma_khu] = thoi_gian_hien_tai

            thoi_diem_bat_dau_chay = state.zone_fire_started_time.get(ma_khu, 0)
            da_canh_bao_dot_chay_nay = state.zone_fire_alerted.get(ma_khu, False)

            if not thoi_diem_bat_dau_chay:
                state.zone_fire_started_time[ma_khu] = thoi_gian_hien_tai
                state.zone_fire_alerted[ma_khu] = False
            else:
                da_du_thoi_gian = (thoi_gian_hien_tai - thoi_diem_bat_dau_chay) >= thoi_gian_dung_chung
                if da_du_thoi_gian and not da_canh_bao_dot_chay_nay:
                    state.zone_fire_alerted[ma_khu] = True
                    state.zone_last_history_time[ma_khu] = thoi_gian_hien_tai

                    ban_ghi_lich_su = GhiLichSuKhu(
                        ma_khu,
                        "detection",
                        "Phát hiện lửa",
                        {
                            "detections": so_luong_phat_hien,
                            "client_id": ma_client,
                            "width": chieu_rong if 'chieu_rong' in locals() else 0,
                            "height": chieu_cao if 'chieu_cao' in locals() else 0,
                            "history_interval": thoi_gian_dung_chung
                        },
                        frame_minh_chung=frame_da_ve
                    )

                    ten_khu = ban_sao_khu_cu.get("name", ma_khu)
                    thoi_gian_canh_bao_text = ban_ghi_lich_su.get("time", LayThoiGianDangChuoi())
                    duong_dan_anh_minh_chung = (ban_ghi_lich_su.get("data") or {}).get("evidence_image", "")

                    # Nếu đã lưu lịch sử detection thì bắt buộc phải bật báo động.
                    BatBaoDongChoKhu(ma_khu)

                    ket_qua_push = GuiCanhBaoDayDenDienThoai(
                        ma_khu=ma_khu,
                        ten_khu=ten_khu,
                        thoi_gian_canh_bao=thoi_gian_canh_bao_text,
                        duong_dan_anh_minh_chung=duong_dan_anh_minh_chung
                    )
                    if not ket_qua_push.get("success", False):
                        print(f"[WARN] Đã lưu lịch sử detection cho {ma_khu} nhưng gửi push chưa thành công: {ket_qua_push}")
        else:
            thoi_diem_thay_lua_cuoi = state.zone_last_fire_seen_time.get(ma_khu, 0)
            da_mat_lua_qua_lau = (thoi_gian_hien_tai - thoi_diem_thay_lua_cuoi) > THOI_GIAN_CHO_PHEP_ROT_DETECTION_GIAY if thoi_diem_thay_lua_cuoi else True
            if da_mat_lua_qua_lau:
                state.zone_fire_started_time[ma_khu] = 0
                state.zone_fire_alerted[ma_khu] = False
                state.zone_last_fire_seen_time[ma_khu] = 0
                TatBaoDongChoKhu(ma_khu)
    else:
        # Dùng lại frame cũ nếu chưa đến lúc chạy AI lại.
        if frame_cu is not None:
            frame_da_ve = frame_cu.copy()
            so_luong_phat_hien = ban_sao_khu_cu.get("detections", 0)
        else:
            frame_da_ve = frame.copy()
            so_luong_phat_hien = 0

    chieu_cao, chieu_rong = frame.shape[:2]
    chuoi_thoi_gian = LayThoiGianDangChuoi()

    # Lưu lại trạng thái mới nhất của khu sau khi xử lý frame.
    with state.state_lock:
        khu = state.zones[ma_khu]
        khu["client_id"] = ma_client
        khu["last_seen"] = thoi_gian_hien_tai
        khu["time"] = chuoi_thoi_gian
        khu["width"] = chieu_rong
        khu["height"] = chieu_cao
        khu["detections"] = so_luong_phat_hien

        state.zone_frames[ma_khu] = frame_da_ve.copy()

    CapNhatCanhBaoAmThanh()

    return {
        "zone_id": ma_khu,
        "client_id": ma_client,
        "width": chieu_rong,
        "height": chieu_cao,
        "detections": so_luong_phat_hien,
        "time": chuoi_thoi_gian,
        "detected": co_nen_chay_nhan_dien,
        "conf_threshold": nguong_tin_cay
    }


def LayFrameTheoKhu(ma_khu):
    # Trả bản sao frame để tránh chỗ khác sửa trực tiếp dữ liệu gốc trong bộ nhớ.
    with state.state_lock:
        frame = state.zone_frames.get(ma_khu)
        return None if frame is None else frame.copy()


def TaoFrameCho(text="Dang cho du lieu..."):
    anh = np.zeros((360, 640, 3), dtype=np.uint8)
    cv2.putText(anh, text, (40, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    return anh


def MaHoaAnhJpg(frame, chat_luong=JPEG_QUALITY):
    # encode = mã hóa ảnh OpenCV sang dữ liệu JPG.
    thanh_cong, du_lieu_da_ma_hoa = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, chat_luong])
    if not thanh_cong:
        return None
    return du_lieu_da_ma_hoa.tobytes()


def TaoLuongMjpeg(ma_khu):
    """Tạo luồng MJPEG liên tục cho route /stream/<zone_id>."""
    while True:
        frame = LayFrameTheoKhu(ma_khu)

        if frame is None:
            frame = TaoFrameCho("Dang cho du lieu...")

        du_lieu_jpg = MaHoaAnhJpg(frame, chat_luong=65)
        if du_lieu_jpg is not None:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + du_lieu_jpg + b"\r\n"
            )

        # Sleep ngắn để luồng stream không ăn CPU quá nhiều.
        time.sleep(STREAM_SLEEP)
