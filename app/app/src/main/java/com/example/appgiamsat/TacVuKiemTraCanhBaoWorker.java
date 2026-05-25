package com.example.appgiamsat;

import android.content.Context;

import androidx.annotation.NonNull;
import androidx.work.Worker;
import androidx.work.WorkerParameters;

import java.util.List;

public class TacVuKiemTraCanhBaoWorker extends Worker {

    public TacVuKiemTraCanhBaoWorker(@NonNull Context context, @NonNull WorkerParameters workerParams) {
        super(context, workerParams);
    }

    @NonNull
    @Override
    public Result doWork() {
        Context context = getApplicationContext();

        try {
            List<Khu> danhSachKhu = TaiDuLieuMang.LayDanhSachKhuTuServer();
            for (Khu khu : danhSachKhu) {
                List<LichSuSuCo> lichSu = TaiDuLieuMang.LayLichSuKhu(khu.getMaKhu());
                if (lichSu == null || lichSu.isEmpty()) {
                    continue;
                }

                LichSuSuCo moiNhat = lichSu.get(0);
                String mocCuoi = BoXuLyThongBao.LayMocThongBaoCuoi(context, khu.getMaKhu());
                String mocMoi = moiNhat.getThoiGian() + "|" + moiNhat.getNoiDung();

                if (!mocMoi.equals(mocCuoi) && moiNhat.getNoiDung() != null && moiNhat.getNoiDung().contains("Phát hiện")) {
                    BoXuLyThongBao.HienThongBaoCanhBao(context, khu.getMaKhu(), khu.getTenKhu(), moiNhat);
                    BoXuLyThongBao.LuuMocThongBaoCuoi(context, khu.getMaKhu(), mocMoi);
                }
            }
            return Result.success();
        } catch (Exception e) {
            return Result.retry();
        }
    }
}
