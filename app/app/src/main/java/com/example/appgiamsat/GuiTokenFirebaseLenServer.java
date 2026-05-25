package com.example.appgiamsat;

import android.content.Context;
import android.util.Log;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class GuiTokenFirebaseLenServer {

    private static final String TAG = "FCM_TOKEN";

    public static void GuiBatDongBo(Context context, String token) {
        if (token == null || token.trim().isEmpty()) {
            Log.e(TAG, "Token rỗng, không gửi lên server");
            return;
        }

        Context appContext = context.getApplicationContext();
        ExecutorService executor = Executors.newSingleThreadExecutor();

        executor.execute(() -> {
            HttpURLConnection ketNoi = null;

            try {
                URL url = new URL(CauHinhServer.API_DANG_KY_FCM_TOKEN);

                ketNoi = (HttpURLConnection) url.openConnection();
                ketNoi.setRequestMethod("POST");
                ketNoi.setConnectTimeout(5000);
                ketNoi.setReadTimeout(5000);
                ketNoi.setDoOutput(true);
                ketNoi.setRequestProperty("Content-Type", "application/json; charset=UTF-8");

                JSONObject json = new JSONObject();
                json.put("token", token);
                json.put("platform", "android");
                json.put("package_name", appContext.getPackageName());

                byte[] duLieu = json.toString().getBytes(StandardCharsets.UTF_8);

                try (OutputStream os = ketNoi.getOutputStream()) {
                    os.write(duLieu);
                    os.flush();
                }

                int maPhanHoi = ketNoi.getResponseCode();
                String noiDungPhanHoi = DocPhanHoi(ketNoi, maPhanHoi);

                Log.d(TAG, "URL đăng ký token: " + CauHinhServer.API_DANG_KY_FCM_TOKEN);
                Log.d(TAG, "Token gửi lên server: " + token);
                Log.d(TAG, "Response code = " + maPhanHoi);
                Log.d(TAG, "Response body = " + noiDungPhanHoi);

                if (maPhanHoi >= 200 && maPhanHoi < 300) {
                    LuuTokenDaGui(appContext, token);
                } else {
                    XoaTokenDaGui(appContext);
                }

            } catch (Exception e) {
                Log.e(TAG, "Lỗi gửi FCM token lên server", e);
                XoaTokenDaGui(appContext);
            } finally {
                if (ketNoi != null) {
                    ketNoi.disconnect();
                }

                executor.shutdown();
            }
        });
    }

    public static void DamBaoTokenDaDangKy(Context context) {
        FirebaseTokenHelper.LayVaDangKyLaiToken(context.getApplicationContext(), false);
    }

    public static boolean CanDangKyLai(Context context, String token) {
        if (token == null || token.trim().isEmpty()) {
            return false;
        }

        String tokenDaGui = context.getSharedPreferences(CauHinhServer.TEN_PREF_FCM, Context.MODE_PRIVATE)
                .getString(CauHinhServer.KHOA_TOKEN_DA_GUI, "");

        return !token.equals(tokenDaGui);
    }

    public static void LuuTokenDaGui(Context context, String token) {
        context.getSharedPreferences(CauHinhServer.TEN_PREF_FCM, Context.MODE_PRIVATE)
                .edit()
                .putString(CauHinhServer.KHOA_TOKEN_DA_GUI, token)
                .apply();
    }

    public static void XoaTokenDaGui(Context context) {
        context.getSharedPreferences(CauHinhServer.TEN_PREF_FCM, Context.MODE_PRIVATE)
                .edit()
                .remove(CauHinhServer.KHOA_TOKEN_DA_GUI)
                .apply();
    }

    private static String DocPhanHoi(HttpURLConnection ketNoi, int maPhanHoi) {
        try {
            InputStream is;

            if (maPhanHoi >= 200 && maPhanHoi < 300) {
                is = ketNoi.getInputStream();
            } else {
                is = ketNoi.getErrorStream();
            }

            if (is == null) {
                return "";
            }

            BufferedReader br = new BufferedReader(
                    new InputStreamReader(is, StandardCharsets.UTF_8)
            );

            StringBuilder sb = new StringBuilder();
            String dong;

            while ((dong = br.readLine()) != null) {
                sb.append(dong);
            }

            br.close();
            return sb.toString();

        } catch (Exception e) {
            return "";
        }
    }
}
