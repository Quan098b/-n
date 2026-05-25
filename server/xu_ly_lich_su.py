"""
xu_ly_lich_su.py
Module lưu và đọc lịch sử theo từng khu.
Nhiệm vụ chính:
- tạo thư mục history nếu chưa có
- ghi sự kiện lịch sử của từng khu ra file riêng
- lưu ảnh minh chứng khi cần
- đọc và xóa lịch sử từng khu cho giao diện server
"""

import json
import os
from datetime import datetime, timezone, timedelta

import cv2

THU_MUC_GOC = os.path.dirname(os.path.abspath(__file__))
THU_MUC_LICH_SU = os.path.join(THU_MUC_GOC, "history")
THU_MUC_MINH_CHUNG = os.path.join(THU_MUC_LICH_SU, "minh_chung")
SO_DONG_TOI_DA_MAC_DINH = 100
MUI_GIO_VIET_NAM = timezone(timedelta(hours=7))


def LayThoiGianVietNam():
    return datetime.now(MUI_GIO_VIET_NAM)


def LayChuoiThoiGianVietNam():
    return LayThoiGianVietNam().strftime("%Y-%m-%d %H:%M:%S")


def DamBaoThuMucLichSuTonTai():
    os.makedirs(THU_MUC_LICH_SU, exist_ok=True)
    os.makedirs(THU_MUC_MINH_CHUNG, exist_ok=True)


def LayDuongDanFileLichSu(ma_khu):
    DamBaoThuMucLichSuTonTai()
    return os.path.join(THU_MUC_LICH_SU, f"{ma_khu}.jsonl")


def LuuAnhMinhChung(ma_khu, frame):
    if frame is None:
        return None

    DamBaoThuMucLichSuTonTai()
    ten_file = f"{ma_khu}_{LayThoiGianVietNam().strftime('%Y%m%d_%H%M%S')}.jpg"
    duong_dan = os.path.join(THU_MUC_MINH_CHUNG, ten_file)

    try:
        cv2.imwrite(duong_dan, frame)
        return {
            "file_name": ten_file,
            "file_path": duong_dan,
            "public_url": f"/history/minh_chung/{ten_file}"
        }
    except Exception:
        return None


def GhiLichSuKhu(ma_khu, loai_su_kien, noi_dung, du_lieu_bo_sung=None, frame_minh_chung=None):
    duong_dan = LayDuongDanFileLichSu(ma_khu)
    duong_dan_anh = LuuAnhMinhChung(ma_khu, frame_minh_chung)

    du_lieu = du_lieu_bo_sung or {}
    if duong_dan_anh:
        du_lieu["evidence_image"] = duong_dan_anh.get("public_url", "")
        du_lieu["evidence_image_file"] = duong_dan_anh.get("file_name", "")

    ban_ghi = {
        "time": LayChuoiThoiGianVietNam(),
        "type": loai_su_kien,
        "message": noi_dung,
        "data": du_lieu
    }

    with open(duong_dan, "a", encoding="utf-8") as tep:
        tep.write(json.dumps(ban_ghi, ensure_ascii=False) + "\n")

    return ban_ghi


def DocLichSuKhu(ma_khu, so_dong_toi_da=SO_DONG_TOI_DA_MAC_DINH):
    duong_dan = LayDuongDanFileLichSu(ma_khu)
    if not os.path.exists(duong_dan):
        return []

    ket_qua = []
    with open(duong_dan, "r", encoding="utf-8") as tep:
        for dong in tep:
            dong = dong.strip()
            if not dong:
                continue
            try:
                ket_qua.append(json.loads(dong))
            except Exception:
                continue

    return list(reversed(ket_qua[-so_dong_toi_da:]))


def XoaLichSuKhu(ma_khu):
    duong_dan = LayDuongDanFileLichSu(ma_khu)
    if os.path.exists(duong_dan):
        os.remove(duong_dan)

    if os.path.exists(THU_MUC_MINH_CHUNG):
        tien_to = f"{ma_khu}_"
        for ten_file in os.listdir(THU_MUC_MINH_CHUNG):
            if ten_file.startswith(tien_to):
                try:
                    os.remove(os.path.join(THU_MUC_MINH_CHUNG, ten_file))
                except Exception:
                    pass
