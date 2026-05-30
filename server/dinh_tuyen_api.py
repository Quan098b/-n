"""
dinh_tuyen_api.py
Module định nghĩa toàn bộ HTTP routes cho server.
Nhiệm vụ chính:
- route trang chủ web
- health check
- API quản lý khu
- API nhận frame từ client
- API trả ảnh JPG và stream MJPEG
"""

from flask import Response, jsonify, render_template, request, send_from_directory
import cv2
import numpy as np

import trang_thai as state
from cau_hinh import DEFAULT_CONF_THRESHOLD
from xu_ly_frame import CapNhatFrameChoKhu, LayFrameTheoKhu, MaHoaAnhJpg, TaoFrameCho, TaoLuongMjpeg
from xu_ly_khu import CapNhatCaiDatKhu, LayAnhChupTrangThaiKhu, ThemKhu, XoaKhu
from xu_ly_lich_su import DocLichSuKhu, GhiLichSuKhu, THU_MUC_MINH_CHUNG, XoaLichSuKhu
from xu_ly_thong_bao_day import DangKyTokenDiDong, LayDanhSachTokenDiDong
#chán quán

def DangKyRoutes(app):
    """Đăng ký toàn bộ routes cho ứng dụng Flask."""

    @app.route("/", methods=["GET"])
    def TrangChu():
        return render_template("index.html")

    @app.route("/api/health", methods=["GET"])
    def KiemTraSucKhoeServer():
        # API nhỏ để kiểm tra nhanh server còn hoạt động hay không.
        return jsonify({"success": True, "status": "ok", "message": "Server đang hoạt động"})

    @app.route("/api/zones", methods=["GET"])
    def LayDanhSachKhu():
        return jsonify({"success": True, "zones": LayAnhChupTrangThaiKhu()})

    @app.route("/api/zones", methods=["POST"])
    def TaoKhuMoi():
        # Đọc dữ liệu JSON mà giao diện/web gửi lên.
        du_lieu = request.get_json(silent=True) or {}
        ten_khu = du_lieu.get("name", "").strip()

        if not ten_khu:
            return jsonify({"success": False, "message": "Tên khu không được để trống."}), 400

        try:
            ma_khu = ThemKhu(ten_khu)
            GhiLichSuKhu(ma_khu, "create_zone", f"Đã tạo khu mới: {ten_khu}")
            return jsonify({
                "success": True,
                "message": "Đã tạo khu mới.",
                "zone": {"id": ma_khu, "name": ten_khu}
            })
        except Exception as loi:
            return jsonify({"success": False, "message": str(loi)}), 500

    @app.route("/api/zones/<ma_khu>", methods=["DELETE"])
    def XoaKhuTheoMa(ma_khu):
        try:
            XoaKhu(ma_khu)
            return jsonify({"success": True, "message": "Đã xóa khu."})
        except KeyError as loi:
            return jsonify({"success": False, "message": str(loi)}), 404
        except RuntimeError as loi:
            return jsonify({"success": False, "message": str(loi)}), 409
        except Exception as loi:
            return jsonify({"success": False, "message": str(loi)}), 500

    @app.route("/api/zones/<ma_khu>/settings", methods=["GET", "POST"])
    def CaiDatKhu(ma_khu):
        if request.method == "GET":
            with state.state_lock:
                if ma_khu not in state.zones:
                    return jsonify({"success": False, "message": "Không tìm thấy khu."}), 404

                khu = state.zones[ma_khu]
                return jsonify({
                    "success": True,
                    "zone": {
                        "id": khu["id"],
                        "name": khu["name"],
                        "conf_threshold": khu.get("conf_threshold", DEFAULT_CONF_THRESHOLD),
                        "history_interval": khu.get("history_interval", 5)
                    }
                })

        du_lieu = request.get_json(silent=True) or {}
        nguong_tin_cay = du_lieu.get("conf_threshold", DEFAULT_CONF_THRESHOLD)
        thoi_gian_luu_anh = du_lieu.get("history_interval", 5)

        try:
            gia_tri_moi, thoi_gian_moi = CapNhatCaiDatKhu(ma_khu, nguong_tin_cay, thoi_gian_luu_anh)
            GhiLichSuKhu(ma_khu, "update_conf", f"Đã cập nhật độ nhạy AI thành {gia_tri_moi:.2f}, thời gian cảnh báo/lưu lịch sử {thoi_gian_moi} giây")
            return jsonify({
                "success": True,
                "message": "Đã cập nhật cài đặt nhận diện.",
                "zone": {"id": ma_khu, "conf_threshold": gia_tri_moi, "history_interval": thoi_gian_moi}
            })
        except KeyError as loi:
            return jsonify({"success": False, "message": str(loi)}), 404
        except Exception as loi:
            return jsonify({"success": False, "message": str(loi)}), 400

    @app.route("/api/zones/<ma_khu>/release", methods=["POST"])
    def NhaKhu(ma_khu):
        du_lieu = request.get_json(silent=True) or {}
        ma_client = du_lieu.get("client_id", "")

        with state.state_lock:
            if ma_khu not in state.zones:
                return jsonify({"success": False, "message": "Không tìm thấy khu."}), 404

            khu = state.zones[ma_khu]
            if not ma_client or khu.get("client_id") == ma_client:
                khu["client_id"] = None
                khu["last_seen"] = 0

        GhiLichSuKhu(ma_khu, "release", "Client đã nhả khu", {"client_id": ma_client})
        return jsonify({"success": True, "message": "Đã nhả khu."})
    #Lấy lịch sử phát hiện cháy của từng khu vực thông qua API /api/zones/<ma_khu>/history
    @app.route("/api/zones/<ma_khu>/history", methods=["GET"])
    def LayLichSuKhu(ma_khu):
        so_dong = request.args.get("limit", default=30, type=int)
        return jsonify({"success": True, "history": DocLichSuKhu(ma_khu, so_dong)})
    # lấy lịch sử phát hiện cháy của từng khu vực trông qua API /api/zones/<ma_khu>/history
    @app.route("/api/zones/<ma_khu>/history", methods=["DELETE"])
    def XoaLichSuTheoKhu(ma_khu):
        XoaLichSuKhu(ma_khu)
        return jsonify({"success": True, "message": "Đã xóa lịch sử khu."})

    @app.route("/history/minh_chung/<ten_file>", methods=["GET"])
    def LayAnhMinhChung(ten_file):
        return send_from_directory(THU_MUC_MINH_CHUNG, ten_file)

    @app.route("/api/mobile/register-token", methods=["POST"])
    def DangKyTokenMobile():
        du_lieu = request.get_json(silent=True) or {}
        token = du_lieu.get("token", "")
        platform = du_lieu.get("platform", "android")
        package_name = du_lieu.get("package_name", "")

        try:
            ban_ghi = DangKyTokenDiDong(token, platform=platform, package_name=package_name)
            return jsonify({
                "success": True,
                "message": "Đã đăng ký token thiết bị.",
                "device": {
                    "platform": ban_ghi.get("platform", "android"),
                    "package_name": ban_ghi.get("package_name", "")
                },
                "total_tokens": len(LayDanhSachTokenDiDong())
            })
        except Exception as loi:
            return jsonify({"success": False, "message": str(loi)}), 400

    @app.route("/api/frame/<ma_khu>", methods=["GET"])
    def LayFrameKhu(ma_khu):
        frame = LayFrameTheoKhu(ma_khu)
        if frame is None:
            frame = TaoFrameCho("Dang cho du lieu...")

        du_lieu_jpg = MaHoaAnhJpg(frame)
        if du_lieu_jpg is None:
            return jsonify({"success": False, "message": "Không mã hóa được ảnh."}), 500

        return Response(du_lieu_jpg, mimetype="image/jpeg")

    @app.route("/stream/<ma_khu>", methods=["GET"])
    def StreamKhu(ma_khu):
        # Trả luồng MJPEG để trình duyệt/giao diện xem ảnh liên tục theo thời gian thực.
        return Response(TaoLuongMjpeg(ma_khu), mimetype="multipart/x-mixed-replace; boundary=frame")

    @app.route("/api/frame", methods=["POST"])
    def NhanFrameTuClient():
        try:
            if "image" not in request.files:
                return jsonify({"success": False, "message": "Thiếu file ảnh. Cần gửi với key là 'image'."}), 400

            ma_khu = request.form.get("zone_id", "").strip()
            ma_client = request.form.get("client_id", "client_01").strip()

            if not ma_khu:
                return jsonify({"success": False, "message": "Thiếu zone_id."}), 400

            tep_anh = request.files["image"]
            # Đọc bytes ảnh client gửi lên.
            du_lieu_anh = tep_anh.read()

            # Chuyển bytes sang mảng số để OpenCV có thể giải mã.
            mang_anh = np.frombuffer(du_lieu_anh, np.uint8)

            # Giải mã dữ liệu ảnh nhận được thành frame OpenCV.
            frame = cv2.imdecode(mang_anh, cv2.IMREAD_COLOR)

            if frame is None:
                return jsonify({"success": False, "message": "Không đọc được frame ảnh."}), 400

            # Cập nhật frame mới của khu và nhận lại kết quả detect/cache.
            ket_qua = CapNhatFrameChoKhu(ma_khu=ma_khu, frame=frame, ma_client=ma_client, co_chay_nhan_dien=True)

            print(
                f"[FRAME] Zone={ket_qua['zone_id']} | Client={ket_qua['client_id']} | "
                f"{ket_qua['width']}x{ket_qua['height']} | detections={ket_qua['detections']} | "
                f"detect={'Y' if ket_qua['detected'] else 'N'} | {ket_qua['time']}"
            )

            return jsonify({"success": True, "message": "Server đã nhận frame.", **ket_qua})

        except KeyError as loi:
            return jsonify({"success": False, "message": str(loi)}), 404
        except RuntimeError as loi:
            thong_bao = str(loi)
            if "chiếm" in thong_bao:
                return jsonify({"success": False, "message": thong_bao}), 409
            return jsonify({"success": False, "message": thong_bao}), 500
        except Exception as loi:
            print(f"[ERROR] {loi}")
            return jsonify({"success": False, "message": str(loi)}), 500
