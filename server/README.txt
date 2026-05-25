README - THU MUC SERVER
======================

1. MUC DICH THU MUC SERVER
-------------------------
Thu muc `server` la phan backend trung tam cua he thong phat hien lua theo khu.
Nhiem vu chinh:
- nhan anh/frame tu cac client camera
- chay AI YOLO de nhan dien lua
- quan ly danh sach khu vuc
- cung cap API cho web, client va app Android
- hien thi giao dien desktop quan ly server
- luu lich su canh bao va anh minh chung
- gui thong bao day len dien thoai
- phat am thanh canh bao tai may server


2. CAC MODULE PYTHON CHINH
--------------------------

2.1. may_chu_lua.py
- La file khoi dong chinh cua server.
- Tao ung dung Flask.
- Dang ky tat ca API routes.
- Nap danh sach khu luc khoi dong.
- Nap token thiet bi di dong da luu.
- Nap model YOLO.
- Chay Flask server o background thread.
- Mo giao dien desktop Tkinter.
- Co ho tro khoi dong Cloudflared tunnel de cong khai server.

Tom lai: day la diem vao chinh de chay toan bo he thong server.


2.2. cau_hinh.py
- Chua toan bo cau hinh dung chung cho server.
- Dinh nghia HOST, PORT.
- Khai bao duong dan model `best.pt`.
- Khai bao duong dan file `zones.json`.
- Cau hinh timeout client, chat luong JPG, tan suat detect, nguong AI mac dinh.

Tom lai: day la noi tap trung cac tham so cau hinh co ban.


2.3. trang_thai.py
- Quan ly trang thai runtime dung chung trong bo nho.
- Luu model da nap.
- Luu danh sach khu.
- Luu frame moi nhat cua tung khu.
- Luu cac moc thoi gian detect, lich su, bao dong.
- Luu token FCM cua dien thoai.
- Co `state_lock` de dong bo du lieu giua nhieu thread.

Tom lai: day la bo nho tam thoi cua he thong khi server dang chay.


2.4. dinh_tuyen_api.py
- Dinh nghia cac HTTP route/API cua Flask.
- Route trang chu web `/`.
- API health check `/api/health`.
- API quan ly khu `/api/zones`.
- API cai dat khu `/api/zones/<ma_khu>/settings`.
- API nhan frame tu client `/api/frame`.
- API tra anh tung khu `/api/frame/<ma_khu>`.
- API stream MJPEG `/stream/<ma_khu>`.
- API lich su tung khu.
- API dang ky token dien thoai nhan thong bao.

Tom lai: day la lop giao tiep giua server va ben ngoai.


2.5. xu_ly_model.py
- Chiu trach nhiem nap model YOLO tu file `best.pt`.
- Chay nhan dien lua tren frame anh.
- Tra ve frame da ve bounding box va so luong vat the phat hien.

Tom lai: day la module AI cot loi cua he thong.


2.6. xu_ly_frame.py
- Xu ly frame anh theo tung khu.
- Nhan frame moi tu client.
- Kiem soat tan suat detect de giam tai CPU/GPU.
- Goi module AI de nhan dien lua.
- Cap nhat thong tin khu: client, thoi gian, kich thuoc, so detection.
- Quan ly logic canh bao: bat dau, duy tri, ket thuc.
- Ghi lich su khi du dieu kien canh bao.
- Goi gui push notification.
- Bat/tat bao dong am thanh.
- Ma hoa anh JPG va tao luong MJPEG.
- Tao frame cho khi chua co du lieu.

Tom lai: day la trung tam xu ly anh va logic canh bao thoi gian thuc.


2.7. xu_ly_khu.py
- Quan ly nghiep vu lien quan den khu/zone.
- Doc va ghi file `zones.json`.
- Tao khu moi.
- Xoa khu.
- Chuan hoa nguong AI va thoi gian luu lich su.
- Kiem tra khu dang bi client chiem hay da het timeout.
- Tao du lieu snapshot de tra cho API va giao dien.

Tom lai: day la module quan ly danh sach khu va trang thai su dung khu.


2.8. xu_ly_lich_su.py
- Quan ly lich su canh bao cua tung khu.
- Tao thu muc `history` neu chua ton tai.
- Ghi su kien vao file `.jsonl` theo tung khu.
- Luu anh minh chung khi co detection.
- Doc lich su de hien thi len giao dien.
- Xoa lich su va cac anh minh chung lien quan.

Tom lai: day la module luu vet cac su kien canh bao.


2.9. xu_ly_thong_bao_day.py
- Quan ly token FCM cua thiet bi di dong.
- Doc/ghi file `mobile_tokens.json`.
- Khoi tao Firebase Admin tu file `baochay.json`.
- Gui push notification khi he thong xac nhan co lua.
- Loai bo token loi neu gui that bai.

Tom lai: day la module thong bao day cho app dien thoai.


2.10. xu_ly_am_thanh.py
- Dieu khien am thanh canh bao tren may server.
- Bat bao dong cho khu dang nguy hiem.
- Duy tri lap lai am thanh khi van con bao dong.
- Tat bao dong sau khi khong con lua.
- Dam bao file am thanh dang phat se phat het, khong cat ngang giua chung.

Tom lai: day la module canh bao bang am thanh cuc bo tren may chu.


2.11. giao_dien_server.py
- Tao giao dien desktop bang Tkinter.
- Hien thi danh sach khu dang giam sat.
- Hien thi anh moi nhat cua tung khu.
- Cho phep them khu, xoa khu.
- Cho phep mo cua so cai dat khu.
- Cho phep xem va xoa lich su tung khu.
- Tu dong goi API de lam moi du lieu dinh ky.

Tom lai: day la giao dien quan tri truc quan cua he thong server.


3. CAC FILE DU LIEU VA TAI NGUYEN QUAN TRONG
-------------------------------------------

3.1. best.pt
- File model YOLO da huan luyen san de nhan dien lua.

3.2. zones.json
- Luu danh sach khu hien co trong he thong.
- Moi khu co ID, ten khu, nguong AI va thoi gian luu lich su/canh bao.

3.3. mobile_tokens.json
- Luu danh sach token FCM cua cac dien thoai da dang ky nhan thong bao.

3.4. baochay.json
- File service account Firebase.
- Duoc dung de server gui thong bao day qua FCM.

3.5. history/
- Thu muc luu lich su su kien theo tung khu.
- Moi khu thuong co mot file `.jsonl` rieng.

3.6. history/minh_chung/
- Luu cac anh minh chung duoc chup tai thoi diem canh bao.

3.7. Am_Thanh/canh_bao.mp3
- File am thanh canh bao phat tren may server.

3.8. templates/index.html
- Giao dien web HTML chinh cua server.

3.9. static/app.js
- Ma JavaScript cho web UI.

3.10. static/style.css
- CSS dinh dang giao dien web.


4. CAC FILE HO TRO CHAY VA HUONG DAN
------------------------------------

4.1. requirements.txt
- Danh sach thu vien Python can cai cho server.

4.2. HUONG_DAN.md
- Huong dan tong quan cach cai dat va chay server.

4.3. HUONG_DAN_CHAY_AN.md
- Huong dan chay server o che do an giao dien hoac an cua so.

4.4. HUONG_DAN_CLOUDFLARE.md
- Huong dan cong khai server qua Cloudflare Tunnel.

4.5. khoi_dong_may_chu.bat
- Script batch de khoi dong server nhanh tren Windows.

4.6. CHAY_AN_GIAO_DIEN.bat
- Script chay server voi cach hien/ an giao dien tuy theo muc dich.

4.7. CHAY_SERVER_CONG_KHAI.bat
- Script chay server theo kieu cong khai.

4.8. chay_cloudflare_cong_khai.bat
- Script lien quan den viec mo tunnel Cloudflare.

4.9. create_startup_task.ps1
- Script tao task khoi dong cung Windows.


5. LUONG HOAT DONG TOM TAT
--------------------------
1. Chay `may_chu_lua.py`.
2. Server nap zones, token FCM va model YOLO.
3. Flask API bat dau lang nghe request.
4. Client gui frame anh len API `/api/frame`.
5. `xu_ly_frame.py` goi `xu_ly_model.py` de detect lua.
6. Neu du dieu kien canh bao:
   - ghi lich su qua `xu_ly_lich_su.py`
   - gui push qua `xu_ly_thong_bao_day.py`
   - phat am thanh qua `xu_ly_am_thanh.py`
7. Web UI, desktop UI va app mobile doc du lieu tu server de hien thi.


6. GOI Y DE HIEU NHANH CAU TRUC SERVER
--------------------------------------
Neu muon doc code theo thu tu de de hieu nhat, nen doc:
1. `may_chu_lua.py`
2. `dinh_tuyen_api.py`
3. `xu_ly_frame.py`
4. `xu_ly_model.py`
5. `xu_ly_khu.py`
6. `xu_ly_lich_su.py`
7. `xu_ly_thong_bao_day.py`
8. `xu_ly_am_thanh.py`
9. `giao_dien_server.py`
10. `trang_thai.py` va `cau_hinh.py`


7. KET LUAN
-----------
Thu muc `server` duoc to chuc theo kieu tach module theo chuc nang:
- module khoi dong
- module cau hinh
- module trang thai runtime
- module API
- module AI
- module xu ly frame
- module quan ly khu
- module lich su
- module thong bao day
- module am thanh
- module giao dien

Cach tach nay giup de bao tri, de sua tung phan va de mo rong he thong trong tuong lai.
