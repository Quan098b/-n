package com.example.appgiamsat;

// Nơi lưu địa chỉ server để app Android gọi API thật.
public class CauHinhServer {

    public static final String SERVER_GOC = "https://api.khanhquan.lol";
    public static final String TEN_PREF_FCM = "fcm_token_pref";
    public static final String KHOA_TOKEN_DA_GUI = "token_da_gui_server";

    public static final String API_DANH_SACH_KHU =
            SERVER_GOC + "/api/zones";

    public static final String API_DANG_KY_FCM_TOKEN =
            SERVER_GOC + "/api/mobile/register-token";

    public static String LayUrlAnhKhu(String maKhu) {
        return SERVER_GOC + "/api/frame/" + maKhu;
    }

    public static String LayUrlLichSuKhu(String maKhu) {
        return SERVER_GOC + "/api/zones/" + maKhu + "/history?limit=30";
    }

    public static String ChuanHoaUrlAnhMinhChung(String duongDanAnh) {
        if (duongDanAnh == null || duongDanAnh.trim().isEmpty()) {
            return "";
        }

        String daChuanHoa = duongDanAnh.replace("\\", "/");

        int viTriHistory = daChuanHoa.indexOf("/history/");
        if (viTriHistory >= 0) {
            return SERVER_GOC + daChuanHoa.substring(viTriHistory);
        }

        if (daChuanHoa.startsWith("http://") || daChuanHoa.startsWith("https://")) {
            return daChuanHoa;
        }

        return "";
    }
}
