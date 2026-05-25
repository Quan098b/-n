package com.example.appgiamsat;

import android.content.Context;
import android.util.Log;

import com.google.firebase.messaging.FirebaseMessaging;

public class FirebaseTokenHelper {
    private static final String TAG = "FCM_TOKEN";

    public static void LayVaDangKyLaiToken(Context context, boolean chiDangKyKhiThayDoi) {
        Context appContext = context.getApplicationContext();

        FirebaseMessaging.getInstance().getToken()
                .addOnSuccessListener(token -> {
                    Log.d(TAG, "Lấy được token: " + token);

                    if (token == null || token.trim().isEmpty()) {
                        Log.e(TAG, "Token FCM rỗng");
                        return;
                    }

                    boolean canGui = !chiDangKyKhiThayDoi || GuiTokenFirebaseLenServer.CanDangKyLai(appContext, token);
                    if (canGui) {
                        GuiTokenFirebaseLenServer.GuiBatDongBo(appContext, token);
                    } else {
                        Log.d(TAG, "Token đã đăng ký trước đó, bỏ qua gửi lại.");
                    }
                })
                .addOnFailureListener(e -> Log.e(TAG, "Không lấy được FCM token", e));
    }
}
