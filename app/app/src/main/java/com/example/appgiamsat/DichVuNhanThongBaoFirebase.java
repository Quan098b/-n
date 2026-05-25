package com.example.appgiamsat;

import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

public class DichVuNhanThongBaoFirebase extends FirebaseMessagingService {

    @Override
    public void onNewToken(String token) {
        super.onNewToken(token);
        GuiTokenFirebaseLenServer.GuiBatDongBo(getApplicationContext(), token);
    }

    @Override
    public void onMessageReceived(RemoteMessage remoteMessage) {
        super.onMessageReceived(remoteMessage);

        String maKhu = remoteMessage.getData().get("zone_id");
        String tenKhu = remoteMessage.getData().get("zone_name");
        String thoiGian = remoteMessage.getData().get("alert_time");
        String anhMinhChung = remoteMessage.getData().get("evidence_image");

        if (maKhu == null || maKhu.trim().isEmpty()) {
            maKhu = "unknown_zone";
        }
        if (tenKhu == null || tenKhu.trim().isEmpty()) {
            tenKhu = "Khu cảnh báo";
        }
        if (thoiGian == null) {
            thoiGian = "";
        }
        if (anhMinhChung == null) {
            anhMinhChung = "";
        }

        LichSuSuCo suCo = new LichSuSuCo(thoiGian, "Phát hiện lửa", anhMinhChung);
        BoXuLyThongBao.HienThongBaoCanhBao(getApplicationContext(), maKhu, tenKhu, suCo);
        BoXuLyThongBao.LuuMocThongBaoCuoi(getApplicationContext(), maKhu, thoiGian + "|push");
        GuiTokenFirebaseLenServer.DamBaoTokenDaDangKy(getApplicationContext());
    }
}
