"""
xu_ly_am_thanh.py
Phát âm thanh cảnh báo trên máy server.
Yêu cầu hiện tại:
- chỉ bắt đầu kêu khi khu đã đủ ngưỡng thời gian phát hiện lửa
- khi đã kêu thì tiếp tục cho tới khi hết nhận diện lửa
- khi chuẩn bị dừng phải phát hết file âm thanh hiện tại, không cắt giữa chừng
- các đợt báo động sau phải kêu lại ổn định
"""

import os
import subprocess
import threading
import time

import trang_thai as state

THU_MUC_GOC = os.path.dirname(os.path.abspath(__file__))
DUONG_DAN_AM_THANH_CANH_BAO = os.path.join(THU_MUC_GOC, "Am_Thanh", "canh_bao.mp3")

_khoa_am_thanh = threading.RLock()
_luong_phat = None
_dang_chay_vong_lap = False


def BatBaoDongChoKhu(ma_khu):
    with state.state_lock:
        state.zone_alarm_active[ma_khu] = True


def TatBaoDongChoKhu(ma_khu):
    with state.state_lock:
        state.zone_alarm_active[ma_khu] = False


def _CoKhuDangBaoDong():
    with state.state_lock:
        return any(bool(dang_bao_dong) for dang_bao_dong in state.zone_alarm_active.values())


def _PhatMotLanVaChoKetThuc():
    lenh = (
        "Add-Type -AssemblyName presentationCore; "
        f"$player = New-Object System.Windows.Media.MediaPlayer; $player.Open([Uri]'{DUONG_DAN_AM_THANH_CANH_BAO}'); "
        "$done = $false; "
        "$player.MediaEnded += { $script:done = $true }; "
        "$player.Play(); "
        "while (-not $done) { Start-Sleep -Milliseconds 200 }"
    )

    startupinfo = None
    creationflags = 0
    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        creationflags = subprocess.CREATE_NO_WINDOW

    tien_trinh = subprocess.Popen(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", lenh],
        startupinfo=startupinfo,
        creationflags=creationflags
    )
    tien_trinh.wait()


def _VongLapPhatCanhBao():
    global _dang_chay_vong_lap, _luong_phat

    try:
        while True:
            if not os.path.exists(DUONG_DAN_AM_THANH_CANH_BAO):
                break

            if not _CoKhuDangBaoDong():
                break

            print("[AUDIO] Bắt đầu phát 1 vòng âm thanh cảnh báo...")
            _PhatMotLanVaChoKetThuc()
            print("[AUDIO] Đã phát xong 1 vòng âm thanh cảnh báo.")

            # Chỉ phát vòng tiếp theo nếu sau khi kết thúc file vẫn còn báo động.
            if not _CoKhuDangBaoDong():
                break

            time.sleep(0.05)
    except Exception as loi:
        print(f"[WARN] Lỗi vòng lặp âm thanh cảnh báo: {loi}")
    finally:
        with _khoa_am_thanh:
            _dang_chay_vong_lap = False
            _luong_phat = None
        print("[AUDIO] Đã dừng vòng lặp âm thanh cảnh báo.")


def CapNhatCanhBaoAmThanh():
    global _dang_chay_vong_lap, _luong_phat

    with _khoa_am_thanh:
        if not os.path.exists(DUONG_DAN_AM_THANH_CANH_BAO):
            return

        dang_bao_dong = _CoKhuDangBaoDong()

        if dang_bao_dong:
            if not _dang_chay_vong_lap or _luong_phat is None or not _luong_phat.is_alive():
                print("[AUDIO] Kích hoạt vòng lặp âm thanh cảnh báo mới.")
                _dang_chay_vong_lap = True
                _luong_phat = threading.Thread(target=_VongLapPhatCanhBao, daemon=True)
                _luong_phat.start()
        else:
            # Không cắt ngang file đang phát. Luồng sẽ tự thoát sau khi phát xong vòng hiện tại.
            print("[AUDIO] Không còn báo động; sẽ dừng sau khi phát hết file hiện tại nếu đang phát.")


def DungCanhBaoAmThanh():
    global _dang_chay_vong_lap
    with _khoa_am_thanh:
        _dang_chay_vong_lap = False
