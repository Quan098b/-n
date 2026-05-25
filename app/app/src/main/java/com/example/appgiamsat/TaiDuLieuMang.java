package com.example.appgiamsat;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

// Lớp hỗ trợ gọi API và tải ảnh thật từ server Flask.
public class TaiDuLieuMang {

    public static List<Khu> LayDanhSachKhuTuServer() throws Exception {
        HttpURLConnection ketNoi = null;
        BufferedReader boDoc = null;

        try {
            URL url = new URL(CauHinhServer.API_DANH_SACH_KHU);
            ketNoi = (HttpURLConnection) url.openConnection();
            ketNoi.setRequestMethod("GET");
            ketNoi.setConnectTimeout(5000);
            ketNoi.setReadTimeout(5000);

            InputStream inputStream = new BufferedInputStream(ketNoi.getInputStream());
            boDoc = new BufferedReader(new InputStreamReader(inputStream, StandardCharsets.UTF_8));

            StringBuilder chuoiJson = new StringBuilder();
            String dong;
            while ((dong = boDoc.readLine()) != null) {
                chuoiJson.append(dong);
            }

            JSONObject jsonGoc = new JSONObject(chuoiJson.toString());
            JSONArray mangKhu = jsonGoc.getJSONArray("zones");

            List<Khu> danhSachKhu = new ArrayList<>();
            for (int i = 0; i < mangKhu.length(); i++) {
                JSONObject obj = mangKhu.getJSONObject(i);

                String maKhu = obj.optString("id", "");
                String tenKhu = obj.optString("name", "Khu");
                boolean dangBiChiem = obj.optBoolean("occupied", false);
                int soPhatHien = obj.optInt("detections", 0);
                String thoiGian = obj.optString("time", "Chưa có");

                String trangThai;
                boolean canhBao = false;
                boolean coDuLieu = true;

                if (thoiGian == null || thoiGian.trim().isEmpty()) {
                    trangThai = "Chưa có dữ liệu";
                    coDuLieu = false;
                } else if (soPhatHien > 0) {
                    trangThai = "Đang hoạt động";
                    canhBao = true;
                } else if (dangBiChiem) {
                    trangThai = "Đang hoạt động";
                } else {
                    trangThai = "Chưa có dữ liệu";
                    coDuLieu = false;
                }

                String moTa = "Dữ liệu lấy trực tiếp từ server";
                String urlAnh = CauHinhServer.LayUrlAnhKhu(maKhu);

                danhSachKhu.add(new Khu(
                        maKhu,
                        tenKhu,
                        trangThai,
                        thoiGian,
                        soPhatHien,
                        moTa,
                        canhBao,
                        coDuLieu,
                        urlAnh
                ));
            }

            return danhSachKhu;
        } finally {
            if (boDoc != null) {
                boDoc.close();
            }
            if (ketNoi != null) {
                ketNoi.disconnect();
            }
        }
    }

    public static List<LichSuSuCo> LayLichSuKhu(String maKhu) throws Exception {
        HttpURLConnection ketNoi = null;
        BufferedReader boDoc = null;

        try {
            URL url = new URL(CauHinhServer.LayUrlLichSuKhu(maKhu));
            ketNoi = (HttpURLConnection) url.openConnection();
            ketNoi.setRequestMethod("GET");
            ketNoi.setConnectTimeout(5000);
            ketNoi.setReadTimeout(5000);

            InputStream inputStream = new BufferedInputStream(ketNoi.getInputStream());
            boDoc = new BufferedReader(new InputStreamReader(inputStream, StandardCharsets.UTF_8));

            StringBuilder chuoiJson = new StringBuilder();
            String dong;
            while ((dong = boDoc.readLine()) != null) {
                chuoiJson.append(dong);
            }

            JSONObject jsonGoc = new JSONObject(chuoiJson.toString());
            JSONArray mangLichSu = jsonGoc.getJSONArray("history");
            List<LichSuSuCo> danhSach = new ArrayList<>();

            for (int i = 0; i < mangLichSu.length(); i++) {
                JSONObject obj = mangLichSu.getJSONObject(i);
                JSONObject data = obj.optJSONObject("data");
                String duongDanAnh = data != null ? data.optString("evidence_image", "") : "";
                danhSach.add(new LichSuSuCo(
                        obj.optString("time", ""),
                        obj.optString("message", ""),
                        duongDanAnh
                ));
            }

            return danhSach;
        } finally {
            if (boDoc != null) {
                boDoc.close();
            }
            if (ketNoi != null) {
                ketNoi.disconnect();
            }
        }
    }

    public static Bitmap TaiAnhBitmap(String duongDanAnh) {
        HttpURLConnection ketNoi = null;
        try {
            URL url = new URL(duongDanAnh);
            ketNoi = (HttpURLConnection) url.openConnection();
            ketNoi.setConnectTimeout(3000);
            ketNoi.setReadTimeout(3000);
            ketNoi.setDoInput(true);
            ketNoi.connect();

            InputStream inputStream = ketNoi.getInputStream();
            return BitmapFactory.decodeStream(inputStream);
        } catch (Exception e) {
            return null;
        } finally {
            if (ketNoi != null) {
                ketNoi.disconnect();
            }
        }
    }
}
