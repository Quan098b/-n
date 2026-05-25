package com.example.appgiamsat;

import java.util.Objects;

// Model dữ liệu đại diện cho một khu giám sát.
public class Khu {
    private final String maKhu;
    private final String tenKhu;
    private final String trangThai;
    private final String thoiGianCapNhat;
    private final int soPhatHien;
    private final String moTa;
    private final boolean canhBao;
    private final boolean coDuLieu;
    private final String urlAnh;

    public Khu(String maKhu, String tenKhu, String trangThai, String thoiGianCapNhat, int soPhatHien,
               String moTa, boolean canhBao, boolean coDuLieu, String urlAnh) {
        this.maKhu = maKhu;
        this.tenKhu = tenKhu;
        this.trangThai = trangThai;
        this.thoiGianCapNhat = thoiGianCapNhat;
        this.soPhatHien = soPhatHien;
        this.moTa = moTa;
        this.canhBao = canhBao;
        this.coDuLieu = coDuLieu;
        this.urlAnh = urlAnh;
    }

    public String getMaKhu() {
        return maKhu;
    }

    public String getTenKhu() {
        return tenKhu;
    }

    public String getTrangThai() {
        return trangThai;
    }

    public String getThoiGianCapNhat() {
        return thoiGianCapNhat;
    }

    public int getSoPhatHien() {
        return soPhatHien;
    }

    public String getMoTa() {
        return moTa;
    }

    public boolean isCanhBao() {
        return canhBao;
    }

    public boolean isCoDuLieu() {
        return coDuLieu;
    }

    public String getUrlAnh() {
        return urlAnh;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Khu)) return false;
        Khu khu = (Khu) o;
        return soPhatHien == khu.soPhatHien
                && canhBao == khu.canhBao
                && coDuLieu == khu.coDuLieu
                && Objects.equals(maKhu, khu.maKhu)
                && Objects.equals(tenKhu, khu.tenKhu)
                && Objects.equals(trangThai, khu.trangThai)
                && Objects.equals(thoiGianCapNhat, khu.thoiGianCapNhat)
                && Objects.equals(urlAnh, khu.urlAnh);
    }

    @Override
    public int hashCode() {
        return Objects.hash(maKhu, tenKhu, trangThai, thoiGianCapNhat, soPhatHien, canhBao, coDuLieu, urlAnh);
    }
}
