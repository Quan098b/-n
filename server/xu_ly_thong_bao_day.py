"""
xu_ly_thong_bao_day.py
Quản lý token FCM và gửi push notification từ server Python.
"""

import json
import os
import time

import trang_thai as state

try:
    import firebase_admin
    from firebase_admin import credentials, messaging
except Exception:
    firebase_admin = None
    credentials = None
    messaging = None

THU_MUC_GOC = os.path.dirname(os.path.abspath(__file__))
DUONG_DAN_SERVICE_ACCOUNT = os.path.join(THU_MUC_GOC, "baochay.json")
DUONG_DAN_TOKENS_FCM = os.path.join(THU_MUC_GOC, "mobile_tokens.json")

_da_khoi_tao_firebase = False


def _DocTokensTuFile():
    if not os.path.exists(DUONG_DAN_TOKENS_FCM):
        return {}

    try:
        with open(DUONG_DAN_TOKENS_FCM, "r", encoding="utf-8") as tep:
            du_lieu = json.load(tep)

        if isinstance(du_lieu, dict):
            return du_lieu
    except Exception as loi:
        print(f"[WARN] Không đọc được file token FCM: {loi}")

    return {}


def _LuuTokensRaFile():
    try:
        with open(DUONG_DAN_TOKENS_FCM, "w", encoding="utf-8") as tep:
            json.dump(state.mobile_fcm_tokens, tep, ensure_ascii=False, indent=2)
    except Exception as loi:
        print(f"[WARN] Không lưu được file token FCM: {loi}")


def NapTokenDiDongDaLuu():
    du_lieu = _DocTokensTuFile()

    if not isinstance(du_lieu, dict):
        return 0

    with state.state_lock:
        state.mobile_fcm_tokens.clear()
        for token, ban_ghi in du_lieu.items():
            if not token:
                continue

            state.mobile_fcm_tokens[token] = {
                "token": token,
                "platform": str((ban_ghi or {}).get("platform", "android") or "android"),
                "package_name": str((ban_ghi or {}).get("package_name", "")).strip(),
                "updated_at": float((ban_ghi or {}).get("updated_at", time.time()) or time.time())
            }

        so_luong = len(state.mobile_fcm_tokens)

    if so_luong > 0:
        print(f"[INFO] Đã nạp {so_luong} token FCM từ file lưu.")

    return so_luong


def DangKyTokenDiDong(token, platform="android", package_name=""):
    token = (token or "").strip()
    if not token:
        raise ValueError("Token không được để trống.")

    with state.state_lock:
        state.mobile_fcm_tokens[token] = {
            "token": token,
            "platform": (platform or "android").strip() or "android",
            "package_name": (package_name or "").strip(),
            "updated_at": time.time()
        }
        ban_ghi = dict(state.mobile_fcm_tokens[token])
        _LuuTokensRaFile()

    print(f"[INFO] Đã đăng ký token thiết bị: platform={ban_ghi.get('platform')} package={ban_ghi.get('package_name')}")
    return ban_ghi


def LayDanhSachTokenDiDong():
    with state.state_lock:
        return list(state.mobile_fcm_tokens.values())


def KhoiTaoFirebaseNeuCan():
    global _da_khoi_tao_firebase

    if _da_khoi_tao_firebase:
        return True

    if firebase_admin is None or credentials is None or messaging is None:
        print("[WARN] Chưa có firebase-admin, chưa thể gửi push FCM.")
        return False

    if not os.path.exists(DUONG_DAN_SERVICE_ACCOUNT):
        print(f"[WARN] Không tìm thấy file service account: {DUONG_DAN_SERVICE_ACCOUNT}")
        return False

    try:
        if not firebase_admin._apps:
            chung_thuc = credentials.Certificate(DUONG_DAN_SERVICE_ACCOUNT)
            firebase_admin.initialize_app(chung_thuc)
        _da_khoi_tao_firebase = True
        return True
    except Exception as loi:
        print(f"[WARN] Không khởi tạo được Firebase Admin: {loi}")
        return False


def GuiCanhBaoDayDenDienThoai(ma_khu, ten_khu, thoi_gian_canh_bao, duong_dan_anh_minh_chung=""):
    if not KhoiTaoFirebaseNeuCan():
        return {"success": False, "message": "Firebase chưa sẵn sàng.", "reason": "firebase_not_ready"}

    danh_sach_token = [muc.get("token", "") for muc in LayDanhSachTokenDiDong() if muc.get("token")]
    if not danh_sach_token:
        print("[INFO] Chưa có token điện thoại nào đăng ký nhận cảnh báo.")
        return {"success": False, "message": "Chưa có token đăng ký.", "reason": "no_registered_tokens"}

    duong_dan_anh = (duong_dan_anh_minh_chung or "").replace("\\", "/")
    if duong_dan_anh and not duong_dan_anh.startswith("http") and "/history/" in duong_dan_anh:
        duong_dan_anh = "https://api.khanhquan.lol" + duong_dan_anh[duong_dan_anh.index("/history/"):]

    du_lieu = {
        "zone_id": str(ma_khu or ""),
        "zone_name": str(ten_khu or ma_khu or "Khu cảnh báo"),
        "alert_time": str(thoi_gian_canh_bao or ""),
        "evidence_image": str(duong_dan_anh or "")
    }

    thanh_cong = 0
    that_bai = 0
    token_loi = []

    for token in danh_sach_token:
        try:
            thong_diep = messaging.Message(
                token=token,
                data=du_lieu,
                android=messaging.AndroidConfig(priority="high")
            )
            messaging.send(thong_diep)
            thanh_cong += 1
        except Exception as loi:
            that_bai += 1
            token_loi.append(token)
            print(f"[WARN] Gửi FCM thất bại cho 1 token: {loi}")

    if token_loi:
        with state.state_lock:
            for token in token_loi:
                state.mobile_fcm_tokens.pop(token, None)
            _LuuTokensRaFile()

    print(f"[INFO] Đã gửi push cảnh báo: success={thanh_cong}, failed={that_bai}")
    return {"success": thanh_cong > 0, "sent": thanh_cong, "failed": that_bai, "reason": "sent" if thanh_cong > 0 else "send_failed"}
