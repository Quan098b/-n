package com.example.appgiamsat;

import android.Manifest;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.os.Build;

import androidx.core.app.ActivityCompat;
import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationManagerCompat;

public class BoXuLyThongBao {
    public static final String TEN_KENH = "canh_bao_lua";
    public static final String TEN_PREF = "thong_bao_lua_pref";
    public static final String KHOA_CUOI = "lich_su_canh_bao_cuoi";

    public static void TaoKenhThongBao(Context context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel kenh = new NotificationChannel(
                    TEN_KENH,
                    "Cảnh báo lửa",
                    NotificationManager.IMPORTANCE_HIGH
            );
            kenh.setDescription("Thông báo khi server phát hiện lửa");
            NotificationManager quanLy = context.getSystemService(NotificationManager.class);
            if (quanLy != null) {
                quanLy.createNotificationChannel(kenh);
            }
        }
    }

    public static void HienThongBaoCanhBao(Context context, String maKhu, String tenKhu, LichSuSuCo lichSu) {
        if (lichSu == null) {
            return;
        }

        TaoKenhThongBao(context);

        Intent intent = new Intent(context, MainActivity.class);
        intent.putExtra("moKhu", maKhu);
        intent.putExtra("tenKhu", tenKhu);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);

        PendingIntent pendingIntent = PendingIntent.getActivity(
                context,
                maKhu.hashCode(),
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        String tieuDe = "Cảnh báo lửa - " + tenKhu;
        String noiDung = lichSu.getThoiGian();

        NotificationCompat.Builder builder = new NotificationCompat.Builder(context, TEN_KENH)
                .setSmallIcon(android.R.drawable.ic_dialog_alert)
                .setContentTitle(tieuDe)
                .setContentText(noiDung)
                .setStyle(new NotificationCompat.BigTextStyle().bigText(noiDung))
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .setAutoCancel(true)
                .setContentIntent(pendingIntent);

        String urlAnh = CauHinhServer.ChuanHoaUrlAnhMinhChung(lichSu.getDuongDanAnhMinhChung());
        if (!urlAnh.isEmpty()) {
            Bitmap bitmap = TaiDuLieuMang.TaiAnhBitmap(urlAnh);
            if (bitmap != null) {
                builder.setStyle(new NotificationCompat.BigPictureStyle()
                        .bigPicture(bitmap)
                        .setBigContentTitle(tieuDe)
                        .setSummaryText(noiDung));
                builder.setLargeIcon(bitmap);
            }
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU
                && ActivityCompat.checkSelfPermission(context, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            return;
        }

        NotificationManagerCompat.from(context).notify((maKhu + lichSu.getThoiGian()).hashCode(), builder.build());
    }

    public static String LayMocThongBaoCuoi(Context context, String maKhu) {
        SharedPreferences pref = context.getSharedPreferences(TEN_PREF, Context.MODE_PRIVATE);
        return pref.getString(KHOA_CUOI + "_" + maKhu, "");
    }

    public static void LuuMocThongBaoCuoi(Context context, String maKhu, String moc) {
        context.getSharedPreferences(TEN_PREF, Context.MODE_PRIVATE)
                .edit()
                .putString(KHOA_CUOI + "_" + maKhu, moc)
                .apply();
    }
}
