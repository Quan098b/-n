"""
state.py
Quản lý trạng thái runtime dùng chung của server:
- model YOLO nhận diện lửa đã nạp
- dữ liệu zone hiện có
- frame mới nhất của từng zone
- mốc thời gian detect gần nhất
- lock để đồng bộ giữa các thread
"""

import threading

# Model AI sau khi đã được nạp vào bộ nhớ.
model = None

# RLock = khóa dùng để nhiều luồng không sửa dữ liệu chung cùng lúc.
state_lock = threading.RLock()

# Danh sách các khu hiện có trong hệ thống.
zones = {}

# Ảnh mới nhất của từng khu, dùng cho web và giao diện server.
zone_frames = {}

# Thời điểm chạy AI nhận diện lửa gần nhất của từng khu để giảm số lần detect.
zone_last_detect_time = {}

# Thời điểm lưu lịch sử phát hiện gần nhất của từng khu.
zone_last_history_time = {}

# Thời điểm một khu bắt đầu có lửa liên tục, dùng để đếm đủ ngưỡng giây mới cảnh báo.
zone_fire_started_time = {}

# Cờ đánh dấu một đợt lửa của khu đã được cảnh báo/lưu lịch sử chưa.
zone_fire_alerted = {}

# Thời điểm khu còn được nhìn thấy có lửa gần nhất; dùng để cho phép rớt detection ngắn mà không reset ngay.
zone_last_fire_seen_time = {}

# Danh sách khu đang ở trạng thái báo động thực sự (đã đủ thời gian và còn đang nhận diện lửa).
zone_alarm_active = {}

# Danh sách token thiết bị di động đã đăng ký nhận cảnh báo.
mobile_fcm_tokens = {}
