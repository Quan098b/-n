# CLIENT - Gửi ảnh camera lên server phát hiện lửa

## Mục đích
Client này mở camera trên máy, chọn một khu trống từ server, rồi gửi frame ảnh liên tục lên server để nhận diện lửa.

## Các file chính
- `giao_dien_client.py` — giao diện desktop của client
- `bo_nhan_dien_lua.py` — logic chính để mở camera và gửi frame

## Cách chạy
### 1. Cài thư viện
```powershell
pip install -r requirements.txt
```

### 2. Chạy giao diện client
```powershell
python giao_dien_client.py
```

## Luồng hoạt động
1. Nhập địa chỉ server
2. Quét camera trên máy
3. Hỏi server để lấy danh sách khu trống
4. Chọn khu
5. Bắt đầu gửi ảnh

## Ghi chú
- Giao diện chỉ hiện tên khu, không hiện ID nội bộ.
- File `bo_nhan_dien_lua.py` là file chính để xử lý logic client.
