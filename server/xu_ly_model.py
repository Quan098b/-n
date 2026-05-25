"""
xu_ly_model.py
Module xử lý mô hình AI.
Nhiệm vụ chính:
- nạp model YOLO từ file best.pt
- chạy nhận diện lửa trên frame đầu vào
"""

import os

from ultralytics import YOLO

import trang_thai as state
from cau_hinh import MODEL_PATH


def NapModel():
    """Nạp model YOLO vào state dùng chung của ứng dụng."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Không tìm thấy model: {MODEL_PATH}")

    state.model = YOLO(MODEL_PATH)
    return state.model


def NhanDienLua(frame, nguong_tin_cay):
    """Chạy nhận diện lửa trên một frame và trả về ảnh đã vẽ + số lượng phát hiện."""
    if state.model is None:
        raise RuntimeError("Model chưa được khởi tạo. Hãy gọi NapModel() trước.")

    ket_qua = state.model.predict(frame, conf=nguong_tin_cay, verbose=False)[0]
    frame_da_ve = ket_qua.plot()
    so_luong_phat_hien = len(ket_qua.boxes) if ket_qua.boxes is not None else 0

    return frame_da_ve, so_luong_phat_hien
