"""
config.py
Khai báo toàn bộ cấu hình dùng chung cho server:
- địa chỉ host/port
- đường dẫn model và file zone
- timeout client
- thông số xử lý ảnh và nhận diện
"""

import os

THU_MUC_GOC = os.path.dirname(os.path.abspath(__file__))

# 0.0.0.0 = cho phép server lắng nghe từ mọi địa chỉ mạng của máy.
HOST = "0.0.0.0"

# Cổng mà Flask server sẽ mở để client/web truy cập vào.
PORT = 5000

# File model AI dùng để nhận diện lửa.
MODEL_PATH = os.path.join(THU_MUC_GOC, "best.pt")

# File JSON dùng để lưu danh sách các khu.
ZONE_FILE = os.path.join(THU_MUC_GOC, "zones.json")

# Nếu client không gửi dữ liệu quá số giây này thì xem như đã ngắt kết nối.
CLIENT_TIMEOUT = 8

# Thời gian nghỉ ngắn giữa các lần đẩy frame MJPEG.
STREAM_SLEEP = 0.05

# Chất lượng JPG mặc định khi mã hóa ảnh.
JPEG_QUALITY = 70

# Khoảng thời gian tối thiểu giữa hai lần chạy AI nhận diện lửa để giảm tải máy.
DETECTION_MIN_INTERVAL = 0.18

# Độ nhạy AI mặc định cho khu mới tạo.
DEFAULT_CONF_THRESHOLD = 0.25

# Chỉ lưu lịch sử phát hiện lửa tối đa 1 lần mỗi 5 giây cho mỗi khu.
LICH_SU_PHAT_HIEN_MOI_GIAY = 5
