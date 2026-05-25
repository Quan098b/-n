# SERVER - Hệ thống giám sát phát hiện lửa theo khu

## Mục đích
Server này nhận ảnh từ các client camera, chạy nhận diện lửa bằng YOLO, rồi hiển thị kết quả theo từng khu.

## Chức năng chính
- Nhận frame ảnh từ client
- Quản lý nhiều khu
- Chạy AI nhận diện lửa
- Hiển thị giao diện desktop và web
- Trả ảnh JPG hoặc stream MJPEG theo từng khu

## Các file chính
- `chay_server.py` — file chạy chính, mở cả Flask server và giao diện desktop
- `config.py` — cấu hình chung
- `state.py` — trạng thái runtime dùng chung
- `xu_ly_model.py` — nạp model và nhận diện AI
- `xu_ly_khu.py` — quản lý khu
- `xu_ly_frame.py` — xử lý frame ảnh
- `dinh_tuyen_api.py` — định nghĩa API
- `giao_dien_server.py` — giao diện desktop của server
- `zones.json` — danh sách khu đang lưu
- `best.pt` — model YOLO

## Cách chạy
### 1. Cài thư viện
```powershell
pip install -r requirements.txt
```

### 2. Chạy server
```powershell
python chay_server.py
```

## Giao diện
Khi chạy `chay_server.py`, chương trình sẽ:
- mở Flask API ở cổng 5000
- mở giao diện desktop Tkinter

Web UI:
- `http://127.0.0.1:5000/`

## API chính
- `GET /api/health` — kiểm tra server
- `GET /api/zones` — lấy danh sách khu
- `POST /api/zones` — tạo khu mới
- `DELETE /api/zones/<ma_khu>` — xóa khu
- `POST /api/frame` — nhận frame từ client
- `GET /api/frame/<ma_khu>` — lấy ảnh mới nhất của khu
- `GET /stream/<ma_khu>` — xem luồng MJPEG của khu

## Ghi chú
- Client chỉ thấy tên khu, không cần biết ID nội bộ.
