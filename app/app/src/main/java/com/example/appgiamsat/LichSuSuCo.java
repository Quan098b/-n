package com.example.appgiamsat;

// Model dữ liệu cho một dòng lịch sử sự cố của khu.
public class LichSuSuCo {
    private final String thoiGian;
    private final String noiDung;
    private final String duongDanAnhMinhChung;

    public LichSuSuCo(String thoiGian, String noiDung) {
        this(thoiGian, noiDung, "");
    }

    public LichSuSuCo(String thoiGian, String noiDung, String duongDanAnhMinhChung) {
        this.thoiGian = thoiGian;
        this.noiDung = noiDung;
        this.duongDanAnhMinhChung = duongDanAnhMinhChung == null ? "" : duongDanAnhMinhChung;
    }

    public String getThoiGian() {
        return thoiGian;
    }

    public String getNoiDung() {
        return noiDung;
    }

    public String getDuongDanAnhMinhChung() {
        return duongDanAnhMinhChung;
    }
}
